import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from hmda.models import HMDARecord
from geo.models import Geo
from geo.views import get_censustract_geoids 
from respondents.models import Institution

def loan_originations(request):
    institution_id = request.GET.get('lender')
    metro = request.GET.get('metro')
    action_taken_param = request.GET.get('action_taken')
    lender_hierarchy = request.GET.get('lh')
    peers = request.GET.get('peers')
    geoids = get_censustract_geoids(request)
    institution_selected = Institution.objects.filter(pk=institution_id).first()
    metro_selected = Geo.objects.filter(geo_type=Geo.METRO_TYPE, geoid=metro).first()
    action_taken_selected = action_taken_param.split(',')
    if geoids and action_taken_selected:
        query = HMDARecord.objects.filter(
                property_type__in=[1,2], owner_occupancy=1, lien_status=1,
                action_taken__in=action_taken_selected)
        if lender_hierarchy == 'true':
            hierarchy_list = Institution.get_lender_hierarchy(institution_selected, False, False)
            if len(hierarchy_list) > 0:
                query = query.filter(institution__in=hierarchy_list) 
            else: 
                query = query.filter(institution__in=institution_selected)
        elif peers == 'true':
            peer_list = Institution.get_peer_list(institution_selected, metro_selected, False, False)
            if len(peer_list) > 0:
                query = query.filter(institution__in=peer_list)
            else:
                query = query.filter(institution=institution_selected)
        else: 
            query = query.filter(institution=institution_selected)
        query = query.filter(geo__geoid__in=geoids)
    else: 
        return HttpResponseBadRequest("Missing one of lender, action_taken, lat/lon bounds or geoid.")
    query = query.values('geo__geoid', 'geo__census2010households__total').annotate(volume=Count('geo__geoid'))
    return query 

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
