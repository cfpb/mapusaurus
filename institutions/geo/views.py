import json
import math

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from topojson import topojson

from geo.models import Geo


def to_lat(zoom, ytile):
    """Convert the /z/x/y parameters to a top-left lat position"""
    n = 2.0 ** zoom
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    return math.degrees(lat_rad)


def to_lon(zoom, xtile):
    """Convert the /z/x/y parameters to a top-left lon position"""
    n = 2.0 ** zoom
    return xtile / n * 360.0 - 180.0


@cache_page(settings.LONGTERM_CACHE_TIMEOUT, cache='long_term_geos')
def tile(request, zoom, xtile, ytile):
    """Get geojson data with no transform"""
    return HttpResponse(geojson(request, zoom, xtile, ytile),
                        content_type='application/json')


@cache_page(settings.LONGTERM_CACHE_TIMEOUT, cache='long_term_geos')
def topotile(request, zoom, xtile, ytile):
    """Convert geojson into topojson"""
    topo_dict = topojson(json.loads(geojson(request, zoom, xtile, ytile)),
                         None)
    return HttpResponse(json.dumps(topo_dict),
                        content_type='application/json')


def geojson(request, zoom, xtile, ytile):
    """A geojson tile which will load the types of geos requested, defaulting
    to county, tract, and metro.

    Much of the conversion logic is based on
    http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat.
    Return all tiles which are inside the requested tile square
    @todo: does it make sense to extend the bounds by a half/quarter in each
    direction?
    """
    geo_types_str = request.GET.get('geo_types', '2,3,4').split(',')
    geo_types = [int(s.strip()) for s in geo_types_str if s.strip().isdigit()]
    #   Safe, due to reges
    zoom, xtile, ytile = int(zoom), int(xtile), int(ytile)
    #   Remove census tracts and counties from high zoom levels
    if zoom <= 8:
        geo_types = [t for t in geo_types if t not in (2, 3)]
    if zoom <= 6:
        geo_types = []

    minlon, maxlon = to_lon(zoom, xtile), to_lon(zoom, xtile + 1)
    minlat, maxlat = to_lat(zoom, ytile + 1), to_lat(zoom, ytile)

    try:
        minlat, maxlat = float(minlat), float(maxlat)
        minlon, maxlon = float(minlon), float(maxlon)
    except ValueError:
        return HttpResponseBadRequest(
            "Bad or missing: one of minlat, maxlat, minlon, maxlon")

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

    shapes = Geo.objects.filter(geo_type__in=geo_types).filter(query)

    # We already have the json strings per model pre-computed, so just place
    # them inside a static response
    response = '{"crs": {"type": "link", "properties": {"href": '
    response += '"http://spatialreference.org/ref/epsg/4326/", "type": '
    response += '"proj4"}}, "type": "FeatureCollection", "features": [%s]}'
    return response % ', '.join(shape.as_geojson() for shape in shapes)


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
