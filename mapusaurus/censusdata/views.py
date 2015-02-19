import json

from django.db.models import Count
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

from hmda.models import HMDARecord
from .models import Census2010RaceStats
from geo.views import get_censustract_geoids
from geo.models import Geo
from djqscsv import render_to_csv_response
from hmda.views import loan_originations_as_json
from respondents.models import Institution

def sum_lar_tuples(tups):
    return sum([tup[1] for tup in tups])

def assemble_stats(lar_data, tracts):
    """
    assembles a lender's applications by those made
    in low, medium and high minority areas;
    we might be assembling stats for a lender or peer;
    """
    lma = []
    mma = []
    hma = []
    for tract in tracts:
        stats = tract.census2010racestats
        if tract.geoid in lar_data.keys():
            tract_tuple = (tract, lar_data[tract.geoid]['volume'])
        else:
            tract_tuple = (tract, 0)
        if stats.total_pop:
            minority = stats.total_pop - stats.non_hisp_white_only
            minority_pct = 1.0 * minority / stats.total_pop
            if minority_pct < .5:
                lma.append(tract_tuple)
            elif minority_pct < .8:
                mma.append(tract_tuple)
            else:
                hma.append(tract_tuple)
    lma_ct = sum_lar_tuples(lma)
    mma_ct = sum_lar_tuples(mma)
    hma_ct = sum_lar_tuples(hma)
    lar_total = lma_ct + mma_ct + hma_ct
    if lar_total:
        lar_stats = {
                'lma': lma_ct, 
                'lma_pct': 1.0 * lma_ct / lar_total, 
                'mma': mma_ct,
                'mma_pct': 1.0 * mma_ct / lar_total,
                'hma': hma_ct,
                'hma_pct': 1.0 * hma_ct / lar_total,
                'lar_total': lar_total
                }
        return lar_stats
    else:
        return {
            'lar_total': 0,
            'lma': 0, 
            'lma_pct': 0, 
            'mma': 0,
            'mma_pct': 0,
            'hma': 0,
            'hma_pct': 0
            }

def tally_msa_minority_stats(tracts):
    """
    metro areas don't have attached census data, 
    so we need to count up minority figures
    """
    pop, minority = 0, 0
    for tract in tracts:
        stats = tract.census2010racestats
        pop += stats.total_pop
        minority += (stats.total_pop - stats.non_hisp_white_only)
    if pop:
        return pop, minority, 1.0 * minority / pop
    else:
        return 0, 0, 0

def combine_peer_stats(collector):
    """
    calculates stats for a group of peers
    """
    peer_total = sum([entry['lar_total'] for entry in collector])
    if peer_total:
        lma = sum([entry['lma'] for entry in collector])
        lma_pct = 1.0 * lma / peer_total
        mma = sum([entry['mma'] for entry in collector])
        mma_pct = 1.0 * mma / peer_total
        hma = sum([entry['hma'] for entry in collector])
        hma_pct = 1.0 * hma / peer_total
        return {
                'lma': lma, 
                'lma_pct': 1.0 * lma / peer_total, 
                'mma': mma,
                'mma_pct': 1.0 * mma / peer_total,
                'hma': hma,
                'hma_pct': 1.0 * hma / peer_total,
                'lar_total': peer_total
                }
    else:
        return {
            'lar_total': 0,
            'lma': 0, 
            'lma_pct': 0, 
            'mma': 0,
            'mma_pct': 0,
            'hma': 0,
            'hma_pct': 0
            }
def minority_aggregation_as_json(request):
    """
    aggregates minority population ranges and LAR counts 
    for a lender in an MSA
    by tract, msa and county
    """
    lar_data = loan_originations_as_json(request)
    lender = Institution.objects.get(institution_id=request.GET.get('lender'))
    tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=request.GET.get('metro'))
    metro = Geo.objects.get(geo_type=Geo.METRO_TYPE, geoid=request.GET.get('metro'))
    lender_stats = assemble_stats(lar_data, tracts)
    # MSA
    msa_pop, msa_minority_ct, msa_minority_pct = tally_msa_minority_stats(tracts)
    msa_stats = {
        'minority_ct': msa_minority_ct,
        'minority_pct': msa_minority_pct
    }
    # PEERS
    peers = lender.get_peer_list(metro)
    if peers:
        peer_data_collector = []
        for peer in peers:
            peer_request = HttpRequest()
            peer_request.GET['lender'] = peer.institution.institution_id
            peer_request.GET['metro']= metro.geoid
            peer_lar_data = loan_originations_as_json(peer_request)
            peer_data_collector.append(assemble_stats(peer_lar_data, tracts))
        if len(peer_data_collector) == 1:
            peer_stats = peer_data_collector[0]
        else:
            peer_stats = combine_peer_stats(peer_data_collector)
        # ODDS
        target_mm = lender_stats['hma'] + lender_stats['mma']
        target_non = lender_stats['lma']
        peer_mm = peer_stats['hma'] + peer_stats['mma']
        peer_non = peer_stats['lma']
        odds = odds_ratio(target_mm, target_non, peer_mm, peer_non)
    else:
        peer_stats = None
        odds = None
    # BY COUNTY -- TODO
    county_ids = sorted(set([tract.geoid[:5] for tract in tracts]))
    county_stats = {county_id: {} for county_id in county_ids}
    for county_id in county_ids:
        county_tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, state=county_id[:2], county=county_id[2:])
        county_stats[county_id] = assemble_stats(lar_data, county_tracts)

    return {
        'msa': msa_stats,
        'lender': lender_stats,
        'peers': peer_stats,
        'odds': odds,
        'counties': county_stats,
        }

def odds_ratio(target_mm, target_non, peer_mm, peer_non):
    """
    calculates odds ratio for a lender compared with peers
    and based on counts of loans in mostly minority areas vs mostly majority areas
    thank you, amy mok
    """
    portfolio_target = float(target_mm) / float(target_mm + target_non)
    portfolio_peer = float(peer_mm) / float(peer_mm + peer_non)

    odds_numer = portfolio_target / (1.0 - portfolio_target)
    odds_denom = portfolio_peer / (1.0 - portfolio_peer)

    return int(odds_numer / odds_denom)

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
