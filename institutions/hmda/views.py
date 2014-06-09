import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest

from hmda.models import HMDARecord


def volume_per_100_households(volume, num_households):
    """Volume of originations can be misleading. Normalize it to some degree
    by considering the number of houses in the same census tract."""
    if num_households:
        return volume * 100.0 / num_households
    else:
        return 0


def loan_originations(request):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""

    state_fips = request.GET.get('state_fips', '')
    county_fips = request.GET.get('county_fips', '')
    lender = request.GET.get('lender', '')

    if state_fips and county_fips and lender:
        records = HMDARecord.objects.filter(
            countyfp=county_fips, lender=lender, statefp=state_fips,
            action_taken__lte=6)    # actions 7-8 are preapprovals to ignore
        query = records.values(
            'geoid', 'geoid__census2010households__total'
        ).annotate(volume=Count('geoid'))
        data = {}
        for row in query:
            data[row['geoid']] = {
                'volume': row['volume'],
                'num_households': row['geoid__census2010households__total'],
                'volume_per_100_households': volume_per_100_households(
                    row['volume'], row['geoid__census2010households__total'])
            }
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponseBadRequest(
            "Missing one of state_fips, county_fips, lender")
