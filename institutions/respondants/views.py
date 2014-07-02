import re

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from haystack.inputs import AutoQuery, Exact
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from respondants.forms import InstitutionSearchForm
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

    if request.method == 'POST':
        form = InstitutionSearchForm(request.POST)
        if form.is_valid():
            name_contains = form.cleaned_data['name_contains']
            return HttpResponseRedirect(
                '/institutions/search/?q=%s' % name_contains)
    else:
        form = InstitutionSearchForm()

    return render(
        request,
        'respondants/index.html',
        {'search_form': form}
    )


class InstitutionSerializer(serializers.ModelSerializer):
    """Used in RESTful endpoints"""
    class Meta:
        model = Institution


@api_view(['GET'])
def search(request):
    query_str = request.GET.get('q', '').strip()
    query = SearchQuerySet().models(Institution).load_all()
    if re.match(r"\d{11}", query_str):
        query = query.filter(lender_id=Exact(query_str))
    elif query_str:
        query = query.filter(content=AutoQuery(query_str))
    else:
        query = []

    results = map(lambda inst: inst.object, query)
    if request.accepted_renderer.format != 'html':
        results = InstitutionSerializer(results, many=True).data

    return Response(
        {'institutions': results},
        template_name='respondants/search_results.html')
