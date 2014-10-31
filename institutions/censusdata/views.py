import json

from django.http import HttpResponse, HttpResponseBadRequest

from .models import Census2010RaceStats
from geo.views import get_censustract_geoids

def race_summary(request):
    """Race summary statistics"""
    northEastLat, northEastLon, southWestLat, southWestLon = request.GET.get('neLat', []), request.GET.get('neLon', [    ]), request.GET.get('swLat', []), request.GET.get('swLon', [])
    geoids = get_censustract_geoids(request, northEastLat, northEastLon, southWestLat, southWestLon)
    if geoids:
        query = Census2010RaceStats.objects.filter(geoid_id__in=geoids)
        return query
    else:
        return HttpResponseBadRequest("Missing geoid or county")


def race_summary_as_json(request_dict):
    records = race_summary(request_dict)
    data = {}
    for stats in records:
        data[stats.geoid_id] = {
            'total_pop': stats.total_pop,
            'hispanic': stats.hispanic,
            'non_hisp_white_only': stats.non_hisp_white_only,
            'non_hisp_black_only': stats.non_hisp_black_only,
            'non_hisp_asian_only': stats.non_hisp_asian_only,
            'hispanic_perc': stats.hispanic_perc,
            'non_hisp_white_only_perc': stats.non_hisp_white_only_perc,
            'non_hisp_black_only_perc': stats.non_hisp_black_only_perc,
            'non_hisp_asian_only_perc': stats.non_hisp_asian_only_perc
        }
    return data



def race_summary_http(request):
    return HttpResponse(json.dumps(race_summary_as_json(request)))
