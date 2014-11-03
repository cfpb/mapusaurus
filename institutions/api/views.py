import json

from django.http import HttpResponse, HttpResponseBadRequest
from geo.views import censustract_data 
from censusdata.views import race_summary_as_json
from hmda.views import loan_originations_as_json


def all(request):
    """This endpoint allows multiple statistical queries to be made in a
    single HTTP request"""
    try:

        hmda = loan_originations_as_json(request)

        minority = race_summary_as_json(request)
        responses = {'minority' : minority, 'loanVolume': hmda }
        return HttpResponse(json.dumps(responses), content_type='application/json')
    except:
        return HttpResponseBadRequest("invalid endpoint")

