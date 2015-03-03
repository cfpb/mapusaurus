import json

from django.db.models import Q
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from hmda.models import HMDARecord
from geo.models import Geo
from geo.views import get_censustract_geos 
from respondents.models import Institution

def base_hmda_query():
    query = Q(property_type__in=[1,2], owner_occupancy=1, lien_status=1)
    return query

def loan_originations(request):
    institution_id = request.GET.get('lender')
    metro = request.GET.get('metro')
    action_taken_param = request.GET.get('action_taken')
    lender_hierarchy = request.GET.get('lh')
    peers = request.GET.get('peers')
    geos = get_censustract_geos(request)
    institution_selected = Institution.objects.get(pk=institution_id)
    metro_selected = Geo.objects.filter(geo_type=Geo.METRO_TYPE, geoid=metro).first()
    if action_taken_param:
        action_taken_selected = action_taken_param.split(',')
    else:
        action_taken_selected = []
    query = HMDARecord.objects.filter(base_hmda_query())
    if action_taken_selected:
        query = query.filter(action_taken__in=action_taken_selected)
    if institution_selected:
        if lender_hierarchy == 'true':
            hierarchy_list = institution_selected.get_lender_hierarchy(False, False)
            if len(hierarchy_list) > 0:
                query = query.filter(institution__in=hierarchy_list) 
            else: 
                query = query.filter(institution=institution_selected)
        elif peers == 'true':
            peer_list = institution_selected.get_peer_list(metro_selected, True, False)
            if len(peer_list) > 0:
                query = query.filter(institution__in=peer_list)
            else:
                query = query.filter(institution=institution_selected)
        else: 
            query = query.filter(institution=institution_selected)
    else:
        return HttpResponseBadRequest("Missing lender")
    if geos is None:
        return HttpResponseBadRequest("Missing one lat/lon bounds or metro.")
    query = query.filter(geo__in=geos)
    query = query.values('geo_id', 'geo__census2010households__total').annotate(volume=Count('geo_id'))
    return query; 

def loan_originations_as_json(request):
    records = loan_originations(request)
    data = {}
    for row in records:
        data[row['geo_id']] = {
            'volume': row['volume'],
            'num_households': row['geo__census2010households__total'],
        }
    return data

def loan_originations_http(request):
    return HttpResponse(json.dumps(loan_originations_as_json(request)))
