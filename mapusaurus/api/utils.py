import json

from django.db.models import Q
from django.http import HttpResponse


def use_GET_in(fn, request):
    """Pass the request's GET dictionary in to fn, using lists for parameters
    that are repeated. If the response is not a dictionary, we know something
    went wrong, so just pass it back. Otherwise, convert the dictionary into a
    json response."""
    get = {}
    for key, value in request.GET.lists():
        get[key] = value
    response = fn(get)
    if isinstance(response, dict):
        return HttpResponse(json.dumps(response),
                            content_type='application/json')
    else:
        return response


def state_county_filter(counties):
    """Given a list of 5-character FIPS codes (two characters designating
    state, three county), generate a sequence of OR'd django Q filters"""
    by_state = {}
    for county in counties:
        state, county = county[:2], county[2:]
        by_state[state] = by_state.get(state, []) + [county]
    query = None
    for state, counties in by_state.iteritems():
        subquery = Q(geoid__state=state, geoid__county__in=counties)
        if query:
            query = query | subquery
        else:
            query = subquery
    return query
