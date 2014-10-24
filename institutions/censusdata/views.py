from django.http import HttpResponseBadRequest

from .models import Census2010RaceStats
from batch.utils import use_GET_in, state_county_filter


def race_summary(request_dict):
    """Race summary statistics"""
    counties = request_dict.get('county', [])
    geoid = request_dict.get('geoid', [])
    if geoid:
        query = Census2010RaceStats.objects.filter(geoid_id__in=geoid)
        data = {}
        for stats in query:
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

    elif counties and all(len(county) == 5 for county in counties):
        query = Census2010RaceStats.objects.filter(
            state_county_filter(counties))
        data = {}
        for stats in query:
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
    else:
        return HttpResponseBadRequest("Missing geoid or county")


def race_summary_http(request):
    return use_GET_in(race_summary, request)
