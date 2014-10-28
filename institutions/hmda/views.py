import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from hmda.models import HMDARecord
from geo.views import get_censustract_geoids 
from rest_framework.renderers import JSONRenderer

def volume_per_100_households(volume, num_households):
    """Volume of originations can be misleading. Normalize it to some degree
    by considering the number of houses in the same census tract."""
    if num_households:
        return volume * 100.0 / num_households
    else:
        return 0


def loan_originations(request_dict, northEastLat, northEastLon, southWestLat, southWestLon, lender, action_taken):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""
    geoid = get_censustract_geoids(request_dict, northEastLat, northEastLon, southWestLat, southWestLon)
    lender = lender
    action_taken = action_taken.split(',')
    if geoid and lender and action_taken:
        query = HMDARecord.objects.filter(
            # actions 7-8 are preapprovals to ignore
            property_type__in=[1,2], owner_occupancy=1, lien_status=1,
            lender=lender, action_taken__in=action_taken
        ).filter(geoid_id__in=geoid).values(
            'geoid', 'geoid__census2010households__total'
        ).annotate(volume=Count('geoid'))
        return query
    else:
        return HttpResponseBadRequest(
            "Missing one of lender, action_taken and county or geoid.")


def loan_originations_as_json(request, northEastLat, northEastLon, southWestLat, southWestLon, lender, action_taken):
    records = loan_originations(request, northEastLat, northEastLon, southWestLat, southWestLon, lender, action_taken)
    data = {}
    for row in records:
        data[row['geoid']] = {
            'volume': row['volume'],
            'num_households': row['geoid__census2010households__total'],
            'volume_per_100_households': volume_per_100_households(row['volume'], row['geoid__census2010households__total'])
        }
    return data



def loan_originations_http(request, northEastLat, northEastLon, southWestLat, southWestLon, lender, action_taken):
    return HttpResponse(json.dumps(loan_originations_as_json(request, northEastLat, northEastLon, southWestLat, southWestLon, lender, action_taken)))
