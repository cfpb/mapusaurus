import json

from django.http import HttpResponse, HttpResponseBadRequest
from geo.views import tract_centroids_as_json 
from geo.models import Geo
from censusdata.views import race_summary_as_json, minority_aggregation_as_json
from hmda.views import loan_originations_as_json
from respondents.views import branch_locations_as_json

def all(request):
    """This endpoint allows multiple statistical queries to be made in a
    single HTTP request"""
    try:
        hmda = loan_originations_as_json(request)
        minority = race_summary_as_json(request)
        responses = {'minority' : minority, 'loanVolume': hmda}
        return HttpResponse(json.dumps(responses), content_type='application/json')
    except:
        return HttpResponseBadRequest("invalid endpoint")

def tables(request):
    try:
        table_data = minority_aggregation_as_json(request)
        context = {'table_data': table_data}
        return HttpResponse(json.dumps(context), content_type='application/json')
    except:
        return HttpResponseBadRequest("invalid endpoint")

def msa(request):
    try:
        metro_id = request.GET.get('metro')
        msa_geo = Geo.objects.get(geo_type=Geo.METRO_TYPE, geoid=metro_id)
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro_id)
    except:
        return HttpResponseBadRequest("invalid endpoint")
    else:
        msa_out = {
         "type": "Feature",
            "geometry": {"type": "Multipolygon", "coordinates": msa_geo.geom.coords},
            "properties": {"metro": msa_geo.geoid, "name": msa_geo.name}
        }
        tracts_out = { 
             "type": "FeatureCollection",
                "features": []
                 }
        for tract in tracts:
            tracts_out['features'].append({
                    "type": "Feature",
                    "geometry": {"type": "Polygon", "coordinates": tract.geom.simplify().coords},
                    "properties": {"tract_id": tract.geoid, "msa_id": tract.cbsa, "centlat": tract.centlat, "centlon": tract.centlon}
                    })
        context = {'msa': msa_out, 'tracts': tracts_out}
        return HttpResponse(json.dumps(context), content_type='application/json')

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
