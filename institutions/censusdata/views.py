import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import numpy as np
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
<<<<<<< HEAD
        raise Http404


def find_bin_indices(field):
    bins = np.array(field['bins'])
    values = np.array(field['values'])
    inds = np.digitize(values, bins)
    return inds


def process_statistics(statreq):
    state_fips = statreq['state_fips']
    county_fips = statreq['county_fips']

    if county_fips and state_fips:

        tract_data = race_by_county(county_fips, state_fips)
        model_fields = [f.name for f in Census2010RaceStats._meta.fields]

        data = {'data': {}}
        bins = {}
        raw_fields = []

        for field in statreq['fields']:
            if field['name'] in model_fields:
                if field['type'] == 'binned':
                    bins[field['name']] = {'values': [], 'bins': field['bins']}
                else:
                    raw_fields.append(field['name'])

        statsids = []
        for stats in tract_data:
            statsids.append(stats.geoid_id)

            for field_name in bins:
                bins[field_name]['values'].append(getattr(stats, field_name))

        for field, vbin in bins.items():
            vbin['bin_indices'] = dict(zip(statsids, find_bin_indices(vbin)))

        for stats in tract_data:
            sdata = {}
            for field in bins:
                field_bin = '%s_bin' % field
                sdata[field_bin] = bins[field]['bin_indices'][stats.geoid_id]

            for field in raw_fields:
                sdata[field] = getattr(stats, field)

            data['data'][stats.geoid_id] = sdata
            data['fields'] = statreq
        return data


@csrf_exempt
def statistics_retriever(request):
    if request.is_ajax():
        statistics_request = json.loads(request.body)
        statistics = process_statistics(statistics_request)
        return HttpResponse(
            json.dumps(statistics), content_type='application/json')
=======
        return HttpResponseBadRequest("Missing one of state_fips, county_fips")
>>>>>>> 9ba3cd18056c902f0c723cddd71218e3fec5e880
