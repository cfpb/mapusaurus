import json

from django.http import HttpResponse, HttpResponseBadRequest

from censusdata.views import race_summary
from hmda.views import loan_originations


# Mapping between requested endpoints (i.e. JS layers) and their handlers
ENDPOINTS = {
    'minority': race_summary,
    'loanVolume': loan_originations
}


def batch(request):
    """This endpoint allows multiple statistical queries to be made in a
    single HTTP request"""
    try:
        params = {}
        for key, value in request.GET.lists():
            params[key] = value
        #   @todo: these should be parallelized
        responses = {}
        for endpoint in params['endpoint']:
            fn = ENDPOINTS[endpoint]
            response = fn(params)
            if isinstance(response, dict):
                responses[endpoint] = response
            else:
                return response     # whole request errors
        return HttpResponse(json.dumps(responses),
                            content_type='application/json')
    except KeyError:
        return HttpResponseBadRequest("invalid endpoint")
