import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest

from hmda.models import HMDARecord
from .models import Census2010RaceStats
from geo.views import get_censustract_geoids, get_tracts_by_msa
from geo.models import Geo
from djqscsv import render_to_csv_response
from hmda.views import loan_originations_as_json

def minority_aggregation_as_json(request):
    """
    aggregates minority population ranges and LAR counts 
    for a lender in an MSA
    TODO: do same by county
    TODO: add odds calc
    """
    tracts = get_tracts_by_msa(request)
    pop, minority = 0, 0
    lma = []
    mma = []
    hma = []
    lma_ct, mma_ct, hma_ct = 0, 0, 0
    for tract in tracts:
        lar_data = loan_originations_as_json(request)
        stats = tract.census2010racestats
        pop += stats.total_pop
        minority += (stats.total_pop - stats.non_hisp_white_only)
        tract_tuple = (tract, lar_data[tract.geoid]['volume'])
        if stats.total_pop:
            minority_pct = 1.0 * (stats.total_pop - stats.non_hisp_white_only) / stats.total_pop
            if minority_pct < .5:
                lma.append(tract_tuple)
            elif minority_pct < .8:
                mma.append(tract_tuple)
            else:
                hma.append(tract_tuple)
    msa_minority_pct = 1.0 * minority / pop
    for tup in lma:
        lma_ct += tup[1]
    for tup in mma:
        mma_ct += tup[1]
    for tup in hma:
        hma_ct += tup[1]
    loan_total = lma_ct + mma_ct + hma_ct
    return {
        'msa_minority_count': minority,
        'msa_minority_pct': msa_minority_pct,
        'msa_population': pop,
        'lender_lma_count': lma_ct,
        'lender_lma_pct': 1.0 * lma_ct / loan_total,
        'lender_mma_count': mma_ct,
        'lender_lma_pct': 1.0 * mma_ct / loan_total,
        'lender_hma_count': hma_ct,
        'lender_hma_pct': 1.0 * hma_ct / loan_total,
    }


def race_summary(request):
    """Race summary statistics"""
    geoids = get_censustract_geoids(request)
    if geoids:
        query = Census2010RaceStats.objects.filter(geoid_id__in=geoids)
        return query
    else:
        return HttpResponseBadRequest("Missing geoid or county")

def race_summary_as_json(request_dict):
    records = race_summary(request_dict)

    data = {}
    for stats in records:
        if stats.total_pop:
            MINPERC = 1.0 * (stats.total_pop - stats.non_hisp_white_only) / stats.total_pop
        else:
            MINPERC = 0
        data[stats.geoid_id] = {
            'total_pop': stats.total_pop,
            'total_pop': stats.total_pop,
            'hispanic': stats.hispanic,
            'non_hisp_white_only': stats.non_hisp_white_only,
            'non_hisp_black_only': stats.non_hisp_black_only,
            'non_hisp_asian_only': stats.non_hisp_asian_only,
            'minority_perc': MINPERC,
            'hispanic_perc': stats.hispanic_perc,
            'non_hisp_white_only_perc': stats.non_hisp_white_only_perc,
            'non_hisp_black_only_perc': stats.non_hisp_black_only_perc,
            'non_hisp_asian_only_perc': stats.non_hisp_asian_only_perc
        }
    return data

def race_summary_http(request):
    return HttpResponse(json.dumps(race_summary_as_json(request)))

def race_summary_csv(request):
    institution_id = request.GET.get('lender')
    metro = request.GET.get('metro')
    action_taken_param = request.GET.get('action_taken')
    action_taken_selected = action_taken_param.split(',')
    tracts_in_msa = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro).values_list('geoid', flat=True)
    query = HMDARecord.objects.filter(institution_id=institution_id, geo_id__in=tracts_in_msa, property_type__in=[1,2], owner_occupancy=1, lien_status=1, action_taken__in=action_taken_selected).values('geo_id', 'geo__census2010households__total', 'geo__census2010racestats__total_pop', 'geo__census2010racestats__hispanic_perc', 'geo__census2010racestats__non_hisp_white_only_perc', 'geo__census2010racestats__non_hisp_black_only_perc', 'geo__census2010racestats__non_hisp_asian_only_perc').annotate(lar_count=Count('geo_id'))
    
    return render_to_csv_response(query)
