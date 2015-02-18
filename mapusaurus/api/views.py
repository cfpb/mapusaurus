import json

from django.http import HttpResponse, HttpResponseBadRequest
from geo.views import tract_centroids_as_json 
from censusdata.views import race_summary_as_json
from hmda.views import loan_originations_as_json
from respondents.views import branch_locations_as_json

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

def hmda(request):
    """This endpoint returns hmda data using params from the request"""
    return HttpResponse(json.dumps(loan_originations_as_json(request)))

def census(request):
    """This endpoint returns census data used for circle coloring over tracts"""
    return HttpResponse(json.dumps(race_summary_as_json(request)))

def tractCentroids(request):
    """This endpoint returns census tract centroids used to determine circle position on map"""
    return HttpResponse(json.dumps(tract_centroids_as_json(request)), content_type='application/json')

def branch_locations(request):
    return HttpResponse(json.dumps(branch_locations_as_json(request)), content_type='application/json')
