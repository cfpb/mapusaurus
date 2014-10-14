from django.db.models import Count
from django.http import HttpResponseBadRequest

from batch.utils import use_GET_in, state_county_filter
from hmda.models import HMDARecord


def volume_per_100_households(volume, num_households):
    """Volume of originations can be misleading. Normalize it to some degree
    by considering the number of houses in the same census tract."""
    if num_households:
        return volume * 100.0 / num_households
    else:
        return 0


def loan_originations(request_dict):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""

    counties = request_dict.get('county', [])
    lender = request_dict.get('lender', [])
    action_taken = request_dict.get('action_taken', [])
    if counties and all(len(c) == 5 for c in counties) and lender:
        query = HMDARecord.objects.filter(
            # actions 7-8 are preapprovals to ignore
            property_type__in=[1,2], owner_occupancy=1,
            loan_purpose=1, lien_status=1,
            lender=lender[0], action_taken__in=action_taken if action_taken else [1,2,3,4,5]
        ).filter(state_county_filter(counties)).values(
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
        return data
    else:
        return HttpResponseBadRequest(
            "Missing one of county or lender")


def loan_originations_http(request):
    return use_GET_in(loan_originations, request)
