import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from geo.views import tract_centroids_as_json, get_censustract_geoids, get_censustract_geos
from geo.models import Geo
from censusdata.views import race_summary_as_json, minority_aggregation_as_json
from hmda.models import HMDARecord
from hmda.views import loan_originations_as_json, loan_originations
from respondents.views import branch_locations_as_json
from django.views.decorators.cache import cache_page

# @cache_page(60 * 360)
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

# @cache_page(60 * 360)
def tables(request):
    try:
        table_data = minority_aggregation_as_json(request)
        context = {'table_data': table_data}
        return HttpResponse(json.dumps(context), content_type='application/json')
    except:
        return HttpResponseBadRequest("the following request failed: %s" % request)

# @cache_page(60 * 360, key_prefix="msas")
def msas(request):
    try:
        query = get_censustract_geos(request, metro=True)
        msas = {
        'msas': [msa.geoid for msa in query]
        }
        return HttpResponse(json.dumps(msas), content_type='application/json')
    except:
        return HttpResponseBadRequest("request failed; details: %s" % request)

# @cache_page(60 * 360, key_prefix="msa")
def msa(request):
    try:
        institution_id = request.GET.get('lender')
        metro = request.GET.get('metro')
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro)
        geoids = tracts.values_list('geoid', flat=True)
        query = HMDARecord.objects.filter(
                property_type__in=[1,2], owner_occupancy=1, lien_status=1,
                geo__geoid__in=geoids, institution__institution_id=institution_id)
        tract_loans = query.values('geo__geoid').annotate(volume=Count('geo__geoid'))
    except:
        return HttpResponseBadRequest("request failed; details: %s" % request)
        tracts_out = { 
             "type": "FeatureCollection",
                "features": []
                 }
        for tract in tract_loans:
            ID = tract['geo__geoid']
            tracts_out['features'].append({
                    "type": "Feature",
                    "geometry": {"type": "Polygon", "coordinates": tracts.get(geoid=ID).geom.simplify(0.001).coords},
                    "properties": {"tract_id": ID, "volume": tract['volume']}
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
