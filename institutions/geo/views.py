import math

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page

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


def tile(geo_type, request, zoom, xtile, ytile):
    """Based on
    http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat.
    Return all tiles which are inside the requested tile square
    @todo: does it make sense to extend the bounds by a half/quarter in each
    direction?
    """
    zoom, xtile, ytile = int(zoom), int(xtile), int(ytile)

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

    shapes = Geo.objects.filter(geo_type=geo_type).filter(query)

    # We already have the json strings per model pre-computed, so just place
    # them inside a static response
    response = '{"crs": {"type": "link", "properties": {"href": '
    response += '"http://spatialreference.org/ref/epsg/4326/", "type": '
    response += '"proj4"}}, "type": "FeatureCollection", "features": [%s]}'
    response = response % ', '.join(shape.as_geojson() for shape in shapes)
    return HttpResponse(response, content_type='application/json')


@cache_page(settings.LONGTERM_CACHE_TIMEOUT, cache='long_term_geos')
def tract_tile(request, zoom, xtile, ytile):
    return tile(Geo.TRACT_TYPE, request, zoom, xtile, ytile)


@cache_page(settings.LONGTERM_CACHE_TIMEOUT, cache='long_term_geos')
def county_tile(request, zoom, xtile, ytile):
    return tile(Geo.COUNTY_TYPE, request, zoom, xtile, ytile)
