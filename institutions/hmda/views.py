from django.db.models import Count, Q
from django.http import HttpResponseBadRequest

from batch.conversions import use_GET_in
from hmda.models import HMDARecord


def volume_per_100_households(volume, num_households):
    """Volume of originations can be misleading. Normalize it to some degree
    by considering the number of houses in the same census tract."""
    if num_households:
        return volume * 100.0 / num_households
    else:
        return 0


def originations_by_county(counties, lender):
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

    # actions 7-8 are preapprovals to ignore
    return HMDARecord.objects.filter(
        lender=lender, action_taken__lte=6
        ).filter(query).values(
        'geoid', 'geoid__census2010households__total'
        ).annotate(volume=Count('geoid'))


def loan_originations(request_dict):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""

    counties = request_dict.get('county', [])
    lender = request_dict.get('lender', '')

    if counties and all(len(c) == 5 for c in counties) and lender:
        query = originations_by_county(counties, lender)
        data = {}
        for row in query:
            data[row['geoid']] = {
                'volume': row['volume'],
                'num_households': row['geoid__census2010households__total'],
                'volume_per_100_households': volume_per_100_households(
                    row['volume'], row['geoid__census2010households__total'])
            }
        return data
    else:
        return HttpResponseBadRequest(
            "Missing one of state_fips, county_fips, lender")


def loan_originations_http(request):
    return use_GET_in(loan_originations, request)
