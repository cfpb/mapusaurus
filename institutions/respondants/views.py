import re

from django.shortcuts import render, get_object_or_404
from django.template import defaultfilters
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


def index(request):
    """  The main view. Display the institution search box here. """

    return render(request, 'respondants/index.html')


class InstitutionSerializer(serializers.ModelSerializer):
    """Used in RESTful endpoints"""
    formatted_name = serializers.SerializerMethodField("format_name")

    def format_name(self, institution):
        formatted = defaultfilters.title(institution.name) + " (0"
        formatted += str(institution.agency_id) + "-" + institution.ffiec_id
        formatted += ")"
        return formatted

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
def search(request):
    query_str = request.GET.get('q', '').strip()
    lender_id = False
    for regex in LENDER_REGEXES:
        match = regex.match(query_str)
        if match:
            lender_id = match.group('agency') + match.group('respondent')

    query = SearchQuerySet().models(Institution).load_all()

    if request.GET.get('sort') in ('assets', '-assets', 'num_loans',
                                   '-num_loans'):
        query = query.order_by(request.GET.get('sort', 'score'))

    if lender_id:
        query = query.filter(lender_id=Exact(lender_id))
    elif query_str and request.GET.get('auto'):
        query = query.filter(text_auto=AutoQuery(query_str))
    elif query_str:
        query = query.filter(content=AutoQuery(query_str))
    else:
        query = []
    query = query[:25]

    results = []
    for result in query:
        result.object.num_loans = result.num_loans
        results.append(result.object)
    if request.accepted_renderer.format != 'html':
        results = InstitutionSerializer(results, many=True).data

    return Response(
        {'institutions': results, 'query_str': query_str},
        template_name='respondants/search_results.html')
