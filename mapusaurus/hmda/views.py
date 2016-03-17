import json
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Count
from django.http import HttpResponse
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
    year = request.GET.get('year')
    census_tracts = get_censustract_geos(request)

    query = HMDARecord.objects.all()
    if institution_id:
        institution_selected = get_object_or_404(Institution, pk=institution_id)
        if lender_hierarchy == 'true':
            hierarchy_list = institution_selected.get_lender_hierarchy(False, False, year)
            if len(hierarchy_list) > 0:
                query = query.filter(institution__in=hierarchy_list)
            else: 
                query = query.filter(institution=institution_selected)
        elif peers == 'true' and metro:
            metro_selected = Geo.objects.filter(geo_type=Geo.METRO_TYPE, geoid=metro).first()
            peer_list = institution_selected.get_peer_list(metro_selected, True, False)
            if len(peer_list) > 0:
                query = query.filter(institution__in=peer_list)
            else:
                query = query.filter(institution=institution_selected)
        else: 
            query = query.filter(institution=institution_selected)
    
    if len(census_tracts) > 0:
        query = query.filter(geo__in=census_tracts)

    if action_taken_param:
        action_taken_selected = action_taken_param.split(',')
        if action_taken_selected:
            query = query.filter(action_taken__in=action_taken_selected)

    #count on geo_id
    query = query.values('geo_id', 'geo__census2010households__total', 'geo__centlat', 'geo__centlon',
                         'geo__state', 'geo__county', 'geo__tract').annotate(volume=Count('geo_id'))
    return query; 

def loan_originations_as_json(request):
    records = loan_originations(request)
    data = {}
    if records:
        for row in records:
            tract_id = row['geo__state']+row['geo__county']+row['geo__tract']
            data[row['geo_id']] = {
                'geoid': row['geo_id'],
                'tractid': tract_id,
                'volume': row['volume'],
                'num_households': row['geo__census2010households__total'],
                'centlat': row['geo__centlat'],
                'centlon': row['geo__centlon'],
            }
    return data

def loan_originations_http(request):
    json_data = loan_originations_as_json(request)
    if json_data:
        return HttpResponse(json.dumps(json_data))
