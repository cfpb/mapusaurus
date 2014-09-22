import re

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from haystack.inputs import AutoQuery, Exact
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from respondants.models import Institution


def respondant(request, agency_id, respondent):
    respondant = get_object_or_404(Institution, ffiec_id=respondent,
                                   agency_id=int(agency_id))
    context = {'respondant': respondant}

    parents = [respondant]

    p = respondant.parent
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
        'respondants/respondant_profile.html',
        context
    )


def search_home(request):
    """Search for an institution"""
    return render(request, 'respondants/search_home.html', {
        'contact_us_email': settings.CONTACT_US_EMAIL
    })


def select_metro(request, agency_id, respondent):
    """Once an institution is selected, search for a metro"""
    institution = get_object_or_404(Institution, ffiec_id=respondent,
                                    agency_id=int(agency_id))
    return render(request, 'respondants/metro_search.html', {
        'institution': institution
    })


class InstitutionSerializer(serializers.ModelSerializer):
    """Used in RESTful endpoints"""
    formatted_name = serializers.CharField(source="formatted_name")

    class Meta:
        model = Institution


# 90123456789
SMASH_RE = re.compile(r"^(?P<agency>[0-9])(?P<respondent>[0-9-]{10})$")
# 09-0123456789
PREFIX_RE = re.compile(r"^0(?P<agency>[0-9])-(?P<respondent>[0-9-]{10})$")
# Some Bank (09-0123456789) - same format as InstitutionSerializer
PAREN_RE = re.compile(r"^.*\(0(?P<agency>[0-9])-(?P<respondent>[0-9-]{10})\)$")
# 0123456789-09
SUFFIX_RE = re.compile(r"^(?P<respondent>[0-9-]{10})-0(?P<agency>[0-9])$")
LENDER_REGEXES = [SMASH_RE, PREFIX_RE, PAREN_RE, SUFFIX_RE]


@api_view(['GET'])
def search_results(request):
    query_str = request.GET.get('q', '').strip()
    lender_id = False
    for regex in LENDER_REGEXES:
        match = regex.match(query_str)
        if match:
            lender_id = match.group('agency') + match.group('respondent')

    query = SearchQuerySet().models(Institution).load_all()

    current_sort = request.GET.get('sort')
    if current_sort in ('assets', '-assets', 'num_loans', '-num_loans'):
        query = query.order_by(current_sort)
    else:
        #sort by bank name by defult since relevance is not very helpful when there is such little text
        current_sort = 'text' 
        query = query.order_by(current_sort)

    if lender_id:
        query = query.filter(lender_id=Exact(lender_id))
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

    sort = request.GET.get('sort', 'relevance')

    total_results = len(query)

    # total number of pages
    if total_results <= num_results:
        total_pages = 1
    else:
        total_pages = total_results / num_results

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
        template_name='respondants/search_results.html')
