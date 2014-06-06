import json

from django.http import HttpResponse, HttpResponseBadRequest

from .models import Census2010RaceStats


def race_by_county(county_fips, state_fips):
    """ Get race summary statistics by county (specified by FIPS codes). """

    tract_data = Census2010RaceStats.objects.filter(
        geoid__statefp=state_fips, geoid__countyfp=county_fips)
    return tract_data


def race_summary(request):
    """ Get race summary statistics. """
    county_fips = request.GET.get('county_fips', '')
    state_fips = request.GET.get('state_fips', '')

    if county_fips and state_fips:
        data = {}
        for stats in race_by_county(county_fips, state_fips):
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
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponseBadRequest("Missing one of state_fips, county_fips")
