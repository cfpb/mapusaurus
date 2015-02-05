import json

from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from geo.models import Geo
from respondents.models import Institution

def tract_centroids_as_json(request):
    return json.loads(tract_centroids_in_json_format(request))

def tract_centroids_in_json_format(request):
    censusgeos = get_censustract_geos(request)
    # We already have the json strings per model pre-computed, so just place
    # them inside a static response
    response = '{"crs": {"type": "link", "properties": {"href": '
    response += '"http://spatialreference.org/ref/epsg/4326/", "type": '
    response += '"proj4"}}, "type": "FeatureCollection", "features": [%s]}'
    return response % ', '.join(geo.tract_centroids_as_geojson() for geo in censusgeos)

def get_censustract_geoids(request):
    if 'neLat' in request.GET:
        geos = get_censustract_geos(request)
    else:
        geos = get_tracts_by_msa(request)
    return geos.values_list('geoid', flat=True)

def get_tracts_by_msa(request):
    msa_id = request.GET.get('metro')
    lender_id = request.GET.get('lender')
    metro = Geo.objects.filter(geo_type=Geo.METRO_TYPE, geoid=msa_id).first()
    lender = Institution.objects.filter(institution_id=lender_id).first()
    if metro and lender:
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=msa_id)
        return tracts
    else:
        return []

def get_censustract_geos(request):
    """ """
    geoTypeId = 3
    northEastLat = request.GET.get('neLat')
    northEastLon = request.GET.get('neLon')
    southWestLat = request.GET.get('swLat')
    southWestLon = request.GET.get('swLon')
    try:
        maxlat, minlon, minlat, maxlon = float(northEastLat), float(southWestLon), float(southWestLat), float(northEastLon)
    except ValueError:
        return HttpResponseBadRequest(
                "Bad or missing values: northEastLat, northEastLon, southWestLat, southWestLon")
    # check that any of the four points or center are inside the boundary
    query = Q(minlat__gte=minlat, minlat__lte=maxlat,
              minlon__gte=minlon, minlon__lte=maxlon)
    query = query | Q(minlat__gte=minlat, minlat__lte=maxlat,
                      maxlon__gte=minlon, maxlon__lte=maxlon)
    query = query | Q(maxlat__gte=minlat, maxlat__lte=maxlat,
                      minlon__gte=minlon, minlon__lte=maxlon)
    query = query | Q(maxlat__gte=minlat, maxlat__lte=maxlat,
                      maxlon__gte=minlon, maxlon__lte=maxlon)
    query = query | Q(centlat__gte=minlat, centlat__lte=maxlat,
                      centlon__gte=minlon, centlon__lte=maxlon)
    geos = Geo.objects.filter(geo_type = geoTypeId).filter(query)
    return geos

class GeoSerializer(serializers.ModelSerializer):
    """Used in RESTful endpoints to serialize Geo objects; used in search"""
    class Meta:
        model = Geo
        fields = ('geoid', 'geo_type', 'name', 'centlat', 'centlon')


@api_view(['GET'])
@renderer_classes((JSONRenderer, ))     # until we need HTML
def search(request):
    query_str = request.GET.get('q', '').strip()
    query = SearchQuerySet().models(Geo).load_all()
    if request.GET.get('auto'):
        query = query.filter(text_auto=AutoQuery(query_str))
    else:
        query = query.filter(content=AutoQuery(query_str))
    query = query[:25]
    results = [result.object for result in query]
    results = GeoSerializer(results, many=True).data

    return Response({'geos': results})
