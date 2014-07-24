import json

from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import numpy as np

from .models import Census2010RaceStats
from batch.conversions import use_GET_in


def race_by_county(counties):
    """ Get race summary statistics by county (specified by FIPS codes). """
    by_state = {}
    for county in counties:
        state, county = county[:2], county[2:]
        by_state[state] = by_state.get(state, []) + [county]

    query = None
    for state, counties in by_state.iteritems():
        subquery = Q(geoid__state=state, geoid__county__in=counties)
        if query:
            query = query | subquery
        else:
            query = subquery

    return Census2010RaceStats.objects.filter(query)


def race_summary(request_dict):
    """Race summary statistics"""
    counties = request_dict.get('county', [])

    if counties and all(len(county) == 5 for county in counties):
        data = {}
        for stats in race_by_county(counties):
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
        return HttpResponseBadRequest("Missing county or county is not len 5")


def race_summary_http(request):
    return use_GET_in(race_summary, request)


def find_bin_indices(field):
    """ Given a dictionary that contains a bins specification and a
    list of values to bin, digitize/bin those values. """

    bins = np.array(field['bins'])
    values = np.array(field['values'])
    inds = np.digitize(values, bins)
    return inds


def split_binned_and_raw_fields(requested_fields):
    """ When we get a specification for the fields that are requested
    (requested_fields), split out the ones that need to be binned, and
    pre-process them a bit. """

    model_fields = [f.name for f in Census2010RaceStats._meta.fields]

    bins = {}
    raw_fields = []
    for field in requested_fields:
        if field['name'] in model_fields:
            if field['type'] == 'binned':
                bins[field['name']] = {'values': [], 'bins': field['bins']}
            else:
                raw_fields.append(field['name'])
    return (bins, raw_fields)


def collect_field_values(tract_data, bins):
    """ For a field that needs to be binned, iterate through the tracts
    and create a single array of all the values. """

    statsids = []
    for stats in tract_data:
        statsids.append(stats.geoid_id)

        for field_name in bins:
            bins[field_name]['values'].append(getattr(stats, field_name))
    return bins, statsids


def find_all_bin_indices(bins, statsids):
    """ For all fields that need to be binned, bin the values. """

    for field, vbin in bins.items():
        vbin['bin_indices'] = dict(zip(statsids, find_bin_indices(vbin)))
    return bins


def process_statistics(statreq):
    """ Process the request for statistics."""
    state_fips = statreq['state_fips']
    county_fips = statreq['county_fips']

    if county_fips and state_fips:
        tract_data = race_by_county(county_fips, state_fips)

        data = {'data': {}}

        bins, raw_fields = split_binned_and_raw_fields(statreq['fields'])
        bins, statsids = collect_field_values(tract_data, bins)
        bins = find_all_bin_indices(bins, statsids)

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
    """ Using a JSON body in a POST request, the user can specify which fields
    are required, whether they need to be binned or not, and how to bin them.
    """

    if request.is_ajax():
        statistics_request = json.loads(request.body)
        statistics = process_statistics(statistics_request)
        return HttpResponse(
            json.dumps(statistics), content_type='application/json')
