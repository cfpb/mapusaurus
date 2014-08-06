import re

from django.shortcuts import render, get_object_or_404
from haystack.inputs import AutoQuery, Exact
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from respondants.models import Institution


def respondant(request, respondant_id):
    respondant = get_object_or_404(Institution, pk=respondant_id)
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
        'respondants/respondant.html',
        context
    )


def search_home(request):
    """Search for an institution"""
    return render(request, 'respondants/index.html')


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
        current_sort = 'score'

    if lender_id:
        query = query.filter(lender_id=Exact(lender_id))
    elif query_str and request.GET.get('auto'):
        query = query.filter(text_auto=AutoQuery(query_str))
    elif query_str:
        query = query.filter(content=AutoQuery(query_str))
    else:
        query = []

    num_results = request.GET.get('num_results')
    if not num_results:
        num_results = 25
    else:
        num_results = int(num_results)

    page = request.GET.get('page')
    if not page:
        page = 1
    else:
        page = int(page)

    if page > 1:
        start_results = num_results * page - num_results
        end_results = num_results * page
    else:
        start_results = 0
        end_results = num_results

    sort = request.GET.get('sort')
    if not sort:
        sort = 'relevance'

    total_results = len(query)
    query = query[start_results:end_results]

    results = []
    for result in query:
        result.object.num_loans = result.num_loans
        results.append(result.object)
    if request.accepted_renderer.format != 'html':
        results = InstitutionSerializer(results, many=True).data

    # to adjust for template
    if start_results == 0:
        start_results = 1

    return Response(
        {'institutions': results, 'query_str': query_str,
         'num_results': num_results, 'start_results': start_results,
         'end_results': end_results, 'sort': sort,
         'next_page': page + 1, 'prev_page': page - 1,
         'page_num': page, 'total_results': total_results,
         'current_sort': current_sort},
        template_name='respondants/search_results.html')
