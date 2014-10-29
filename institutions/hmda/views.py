import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from hmda.models import HMDARecord
from geo.views import get_censustract_geoids 
from rest_framework.renderers import JSONRenderer


def loan_originations(request):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""
    northEastLat, northEastLon, southWestLat, southWestLon = request.GET.get('neLat'), request.GET.get('neLon', []), request.GET.get('swLat', []), request.GET.get('swLon', [])
    geoids = get_censustract_geoids(request, northEastLat, northEastLon, southWestLat, southWestLon)
    lender = request.GET.get('lender', [])
    action_taken_param = request.GET.get('action_taken', [])
    action_taken = action_taken_param.split(',')
    if geoids and lender and action_taken:
        query = HMDARecord.objects.filter(
            # actions 7-8 are preapprovals to ignore
            property_type__in=[1,2], owner_occupancy=1, lien_status=1,
            lender=lender, action_taken__in=action_taken
        ).filter(geoid_id__in=geoids).values(
            'geoid', 'geoid__census2010households__total'
        ).annotate(volume=Count('geoid'))
        return query
    else:
        return HttpResponseBadRequest("Missing one of lender, action_taken and county or geoid.")

def loan_originations_as_json(request):
    records = loan_originations(request)
    data = {}
    for row in records:
        data[row['geoid']] = {
            'volume': row['volume'],
            'num_households': row['geoid__census2010households__total'],
        }
    return data



def loan_originations_http(request):
    return HttpResponse(json.dumps(loan_originations_as_json(request)))
