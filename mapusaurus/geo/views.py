import json

from django.db.models import Q
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from geo.models import Geo
from geo.utils import check_bounds

def geo_as_json(geos):
    return json.loads(format_geo_to_geojson(geos))

def format_geo_to_geojson(geos):
    # We already have the json strings per model pre-computed, so just place
    # them inside a static response
    response = '{"crs": {"type": "link", "properties": {"href": '
    response += '"http://spatialreference.org/ref/epsg/4326/", "type": '
    response += '"proj4"}}, "type": "FeatureCollection", "features": [%s]}'
    return response % ', '.join(geo.tract_centroids_as_geojson() for geo in geos)

def get_censustract_geos(request):
    import pdb; pdb.set_trace()
    northEastLat = request.GET.get('neLat')
    northEastLon = request.GET.get('neLon')
    southWestLat = request.GET.get('swLat')
    southWestLon = request.GET.get('swLon')
    metro = request.GET.get('metro')
    if check_bounds(northEastLat, northEastLon, southWestLat, southWestLon):
        maxlat, minlon, minlat, maxlon = float(northEastLat), float(southWestLon), float(southWestLat), float(northEastLon)
        geos = get_geos_by_bounds_and_type(maxlat, minlon, minlat, maxlon)
    elif metro:
        msa = Geo.objects.get(geo_type=Geo.METRO_TYPE, geoid=metro)
        geos = msa.get_censustract_geos_by_msa()
    return geos

def get_geos_by_bounds_and_type(maxlat, minlon, minlat, maxlon, metro=False):
    """handles requests for tract-level ids or MSA ids"""
    if metro == False:
        geoTypeId = 3
    else:
        geoTypeId = 4
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
