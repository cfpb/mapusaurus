import re
import math
import json
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from haystack.inputs import AutoQuery, Exact
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponseBadRequest
from respondents.models import Institution, Branch


def respondent(request, agency_id, respondent):
    respondent = get_object_or_404(Institution, respondent_id=respondent,
                                   agency_id=int(agency_id))
    context = {'respondent': respondent}

    parents = [respondent]

    p = respondent.parent
    while p:
        parents.append(p)
        p = p.parent

    last = parents[-1]
    if last.non_reporting_parent:
        context['non_reporting_parent'] = last.non_reporting_parent

    parents = parents[1:]
    context['parents'] = reversed(parents)

    return render(
        request,
        'respondents/respondent_profile.html',
        context
    )


def search_home(request):
    """Search for an institution"""
    return render(request, 'respondents/search_home.html', {
        'contact_us_email': settings.CONTACT_US_EMAIL
    })


def select_metro(request, agency_id, respondent):
    """Once an institution is selected, search for a metro"""
    institution = get_object_or_404(Institution, respondent_id=respondent,
                                    agency_id=int(agency_id))
    return render(request, 'respondents/metro_search.html', {
        'institution': institution
    })


class InstitutionSerializer(serializers.ModelSerializer):
    """Used in RESTful endpoints"""
    formatted_name = serializers.CharField(source="formatted_name")

    class Meta:
        model = Institution


# 90123456789 (Agency Code + Respondent ID)
PREFIX_RE = re.compile(r"^(?P<agency>[0-9])(?P<respondent>[0-9-]{10})$")
# Some Bank (90123456789) - same format as InstitutionSerializer
PAREN_RE = re.compile(r"^.*\((?P<agency>[0-9])(?P<respondent>[0-9-]{10})\)$")
# 0123456789 (Respondent ID Only)
RESP_RE = re.compile(r"^(?P<respondent>[0-9-]{10})$")
LENDER_REGEXES = [PREFIX_RE, PAREN_RE]


@api_view(['GET'])
def search_results(request):
    query_str = request.GET.get('q', '').strip()
    lender_id = False
    respondent_id = False
    for regex in LENDER_REGEXES:
        match = regex.match(query_str)
        if match:
            lender_id = match.group('agency') + match.group('respondent')
    resp_only_match = RESP_RE.match(query_str)
    if resp_only_match:
        respondent_id = resp_only_match.group('respondent')
    
    query = SearchQuerySet().models(Institution).load_all()
    
    current_sort = request.GET.get('sort')
    if current_sort == None:
        current_sort = '-assets'

    query = SearchQuerySet().models(Institution).load_all().order_by(current_sort)

    if lender_id:
        query = query.filter(lender_id=Exact(lender_id))
    elif respondent_id:
        query = query.filter(respondent_id=Exact(respondent_id))
    elif query_str and request.GET.get('auto'):
        query = query.filter(text_auto=AutoQuery(query_str))
    elif query_str:
        query = query.filter(content=AutoQuery(query_str))
    else:
        query = []

    # number of results per page
    try:
        num_results = int(request.GET.get('num_results', '25'))
    except ValueError:
        num_results = 25

    # page number
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # start and end results
    if page > 1:
        start_results = num_results * page - num_results
        end_results = num_results * page
    else:
        start_results = 0
        end_results = num_results

    sort = current_sort #request.GET.get('sort', 'relevance')

    total_results = len(query)

    # total number of pages
    if total_results <= num_results:
        total_pages = 1
    else:
        total_pages = int( math.ceil( float(total_results) / float(num_results) ) )

    query = query[start_results:end_results]

    # next page
    if total_results < num_results or page is total_pages:
        next_page = 0
        end_results = total_results
    else:
        next_page = page + 1

    # previous page
    prev_page = page - 1

    results = []
    for result in query:
        result.object.num_loans = result.num_loans
        results.append(result.object)
    if request.accepted_renderer.format != 'html':
        results = InstitutionSerializer(results, many=True).data

    # to adjust for template
    start_results = start_results + 1

    return Response(
        {'institutions': results, 'query_str': query_str,
         'num_results': num_results, 'start_results': start_results,
         'end_results': end_results, 'sort': sort,
         'page_num': page, 'total_results': total_results,
         'next_page': next_page, 'prev_page': prev_page,
         'total_pages': total_pages, 'current_sort': current_sort},
        template_name='respondents/search_results.html')

def branch_locations_as_json(request):
    return json.loads(branch_locations(request))

def branch_locations(request):
    """This endpoint returns geocoded branch locations"""
    lender = request.GET.get('lender')
    northEastLat = request.GET.get('neLat')
    northEastLon = request.GET.get('neLon')
    southWestLat = request.GET.get('swLat')
    southWestLon = request.GET.get('swLon')
    try:
        maxlat, minlon, minlat, maxlon = float(northEastLat), float(southWestLon), float(southWestLat), float(northEastLon)
    except ValueError:
        return HttpResponseBadRequest(
                "Bad or missing values: northEastLat, northEastLon, southWestLat, southWestLon")
    # check that any of the four points or center are inside the boundary
    #query = Q(minlat__gte=minlat, minlat__lte=maxlat,
    #          minlon__gte=minlon, minlon__lte=maxlon)
    #query = query | Q(minlat__gte=minlat, minlat__lte=maxlat,
    #                  maxlon__gte=minlon, maxlon__lte=maxlon)
    #query = query | Q(maxlat__gte=minlat, maxlat__lte=maxlat,
    #                  minlon__gte=minlon, minlon__lte=maxlon)
    #query = query | Q(maxlat__gte=minlat, maxlat__lte=maxlat,
    #                  maxlon__gte=minlon, maxlon__lte=maxlon)
    query = Q(lat__gte=minlat, lat__lte=maxlat,
                      lon__gte=minlon, lon__lte=maxlon)
    branches = Branch.objects.filter(institution_id=lender).filter(query)
    response = '{"crs": {"type": "link", "properties": {"href": '
    response += '"http://spatialreference.org/ref/epsg/4326/", "type": '
    response += '"proj4"}}, "type": "FeatureCollection", "features": [%s]}'
    return response % ', '.join(branch.branch_as_geojson() for branch in branches)
