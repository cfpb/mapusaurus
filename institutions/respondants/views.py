import re

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import defaultfilters, RequestContext
from django.template.loader import select_template
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

    context = RequestContext(request, {})
    template = select_template(['respondants/custom-index.html',
                                'respondants/index.html'])
    return HttpResponse(template.render(context))


class InstitutionSerializer(serializers.ModelSerializer):
    """Used in RESTful endpoints"""
    formatted_name = serializers.SerializerMethodField("format_name")

    def format_name(self, institution):
        formatted = defaultfilters.title(institution.name) + " ("
        formatted += str(institution.agency_id) + institution.ffiec_id + ")"
        return formatted

    class Meta:
        model = Institution


@api_view(['GET'])
def search(request):
    query_str = request.GET.get('q', '').strip()
    lender_id = request.GET.get('lender_id')
    # Account for paren lender ids as we might generate elsewhere
    if re.match(r".*\([0-9-]{11}\)$", query_str):
        lparen_pos = query_str.rfind('(')
        lender_id = query_str[lparen_pos + 1:-1]
        query_str = query_str[:lparen_pos]
    elif re.match(r"[0-9-]{11}", query_str):
        lender_id = query_str

    query = SearchQuerySet().models(Institution).load_all()

    if lender_id:
        query = query.filter(lender_id=Exact(lender_id))
    elif query_str and request.GET.get('auto'):
        query = query.filter(text_auto=AutoQuery(query_str))
    elif query_str:
        query = query.filter(content=AutoQuery(query_str))
    else:
        query = []
    query = query[:25]

    results = map(lambda inst: inst.object, query)
    if request.accepted_renderer.format != 'html':
        results = InstitutionSerializer(results, many=True).data

    return Response(
        {'institutions': results},
        template_name='respondants/search_results.html')
