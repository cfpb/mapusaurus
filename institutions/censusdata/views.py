import json

from django.http import HttpResponse, HttpResponseBadRequest

from .models import Census2010RaceStats
from geo.views import get_censustract_geoids

def race_summary(request_dict, northEastLat, northEastLon, southWestLat, southWestLon):
    """Race summary statistics"""
    geoid = get_censustract_geoids(request_dict, northEastLat, northEastLon, southWestLat, southWestLon)
    if geoid:
        query = Census2010RaceStats.objects.filter(geoid_id__in=geoid)
        return query
    else:
        return HttpResponseBadRequest("Missing geoid or county")


def race_summary_as_json(request_dict, northEastLat, northEastLon, southWestLat, southWestLon):
    records = race_summary(request_dict, northEastLat, northEastLon, southWestLat, southWestLon)
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



def race_summary_http(request, northEastLat, northEastLon, southWestLat, southWestLon):
    return HttpResponse(json.dumps(race_summary_as_json(request, northEastLat, northEastLon, southWestLat, southWestLon)))
