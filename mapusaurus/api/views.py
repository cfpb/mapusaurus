import json

from django.http import HttpResponse, HttpResponseBadRequest
from geo.views import geo_as_json, get_geos_by_bounds_and_type, get_censustract_geos
from geo.models import Geo
from censusdata.views import race_summary_as_json, minority_aggregation_as_json
from hmda.views import loan_originations_as_json
from respondents.views import branch_locations_as_json
from geo.utils import check_bounds

def all(request):
    """This endpoint allows multiple statistical queries to be made in a
    single HTTP request"""
    try:
        hmda = loan_originations_as_json(request)
        minority = race_summary_as_json(request)
        responses = {'minority' : minority, 'loanVolume': hmda}
        return HttpResponse(json.dumps(responses), content_type='application/json')
    except:
        return HttpResponseBadRequest("Invalid or Missing one of lender, metro or lat/lon bounds")

def tables(request):
    try:
        table_data = minority_aggregation_as_json(request)
        return HttpResponse(json.dumps(table_data), content_type='application/json')
    except:
        return HttpResponseBadRequest("the following request failed: %s" % request)

def msas(request):
    """return a list of MSA ids visible by bounding coordinates"""
    try:
        northEastLat = request.GET.get('neLat')
        northEastLon = request.GET.get('neLon')
        southWestLat = request.GET.get('swLat')
        southWestLon = request.GET.get('swLon')
        bounds = check_bounds(northEastLat, northEastLon, southWestLat, southWestLon)
        if bounds:
            pass
            #maxlat, minlon, minlat, maxlon = bounds[0], bounds[1], bounds[2], bounds[3]
        msas = get_geos_by_bounds_and_type(*bounds, metro=True)
        msa_list = [metro.geoid for metro in msas]
        return HttpResponse(json.dumps(msa_list), content_type='application/json')
    except:
        return HttpResponseBadRequest("Invalid lat/lon bounding coordinates")

def msa(request):
    """returns simplified tract shapes for dot-density mapping, with loan volume"""
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
                if tract.geoid in tract_loans and isinstance(tract_loans[tract.geoid]['volume'], int):
                    volume += tract_loans[tract.geoid]['volume']
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
    geos = get_censustract_geos(request)
    if geos is None:
        return HttpResponseBadRequest("Missing one of lat/lon bounds or metro")
    tracts_geo_json = geo_as_json(geos)
    return HttpResponse(json.dumps(tracts_geo_json), content_type='application/json')
    
def branch_locations(request):
    return HttpResponse(json.dumps(branch_locations_as_json(request)), content_type='application/json')
