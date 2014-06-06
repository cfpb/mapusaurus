import json

from django.db.models import Count
from django.http import HttpResponse, Http404

from hmda.models import HMDARecord


def loan_originations(request):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""

    state_fips = request.GET.get('state_fips', '')
    county_fips = request.GET.get('county_fips', '')
    lender = request.GET.get('lender', '')

    if state_fips and county_fips and lender:
        records = HMDARecord.objects.filter(
            action_taken__lte=6, lender=lender, statefp=state_fips,
            countyfp=county_fips)
        query = records.values(
            'geoid', 'geoid__census2010households__total'
        ).annotate(volume=Count('geoid'))
        data = {}
        for row in query:
            if row['geoid__census2010households__total'] > 0:
                data[row['geoid']] = {
                    'volume': row['volume'],
                    'volume_per_100_households':
                        row['volume'] * 100.0
                        / row['geoid__census2010households__total']
                }
            else:
                data[row['geoid']] = {
                    'volume': row['volume'],
                    'volume_per_100_households': 0
                }
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404
