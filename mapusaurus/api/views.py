import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from geo.views import tract_centroids_as_json, get_censustract_geoids, get_censustract_geos
from geo.models import Geo
from censusdata.views import race_summary_as_json, minority_aggregation_as_json
from hmda.models import HMDARecord
from hmda.views import loan_originations_as_json, loan_originations
from respondents.views import branch_locations_as_json
# from django.views.decorators.cache import cache_page

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
        return HttpResponseBadRequest("the following request failed: %s" % request)

def msas(request):
    """return a list of MSA ids visible by bounding coordinates"""
    try:
        msas = get_censustract_geos(request, metro=True)
        msa_list = [metro.geoid for metro in msas]
        return HttpResponse(json.dumps(msa_list), content_type='application/json')
    except:
        return HttpResponseBadRequest("Invalid bounding coordinates")

def msa(request):
    try:
        metro = request.GET.get('metro')
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro)
        tract_loans = loan_originations_as_json(request)
    except:
        return HttpResponseBadRequest("request failed; details: %s" % request)
    else:
        try:
            with open("/var/www/static/tracts/%s.json" % metro, 'r') as f:
                local_tracts = json.loads(f.read())
        except:
            local_tracts = None
        tracts_out = { 
             "type": "FeatureCollection",
                "features": []
                 }
        if local_tracts:
            for tract_id in local_tracts:
                volume = 0
                if tract_id in tract_loans and tract_loans[tract_id]['volume']:
                    volume += tract_loans[tract_id]['volume']
                tracts_out['features'].append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": local_tracts[tract_id]},
                        "properties": {"tract_id": tract_id, "volume": volume}
                        })
        else:
            for tract in tracts:
                volume = 0
                if tract.geoid in tract_loans:
                    volume += tract_loans[tract.geoid]
                tracts_out['features'].append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": tract.geom.simplify(0.001).coords},
                        "properties": {"tract_id": tract.geoid, "volume": volume}
                        })
        context = {'tracts': tracts_out}
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
