import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from hmda.models import HMDARecord
from geo.views import get_censustract_geoids 
from rest_framework.renderers import JSONRenderer
from respondents.models import LenderHierarchy, Institution

def loan_originations(request):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""
    lender_id = request.GET.get('lender')
    action_taken_param = request.GET.get('action_taken')
    lender_hierarchy = request.GET.get('lh')
    geoids = get_censustract_geoids(request)
    action_taken = action_taken_param.split(',')
    if lender_hierarchy == 'true':
        lender = Institution.objects.get(institution_id=lender_id)
        lenders = LenderHierarchy.objects.filter(organization_id=lender.lenderhierarchy_set.get().organization_id).values_list('institution_id', flat=True)
        if len(lenders) == 0:
            return HttpResponseRequest("No other lenders found in hierarchy. Invalid lender")
        if geoids and lenders and action_taken:
            query = HMDARecord.objects.filter(
                # actions 7-8 are preapprovals to ignore
                property_type__in=[1,2], owner_occupancy=1, lien_status=1,
                lender__in=lenders, action_taken__in=action_taken
            ).filter(geo__geoid__in=geoids).values(
                'geo__geoid', 'geo__census2010households__total'
            ).annotate(volume=Count('geo__geoid'))
            return query
    elif geoids and lender_id and action_taken:
        query = HMDARecord.objects.filter(
            # actions 7-8 are preapprovals to ignore
            property_type__in=[1,2], owner_occupancy=1, lien_status=1,
            institution_id=lender_id, action_taken__in=action_taken
        ).filter(geo__geoid__in=geoids).values(
            'geo__geoid', 'geo__census2010households__total'
        ).annotate(volume=Count('geo__geoid'))
        return query
    else:
        return HttpResponseBadRequest("Missing one of lender, action_taken and county or geoid.")

def loan_originations_as_json(request):
    records = loan_originations(request)
    data = {}
    for row in records:
        data[row['geo__geoid']] = {
            'volume': row['volume'],
            'num_households': row['geo__census2010households__total'],
        }
    return data

def loan_originations_http(request):
    return HttpResponse(json.dumps(loan_originations_as_json(request)))
