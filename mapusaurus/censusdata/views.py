import json
import csv
from django.utils.encoding import smart_str
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

from hmda.models import HMDARecord
from .models import Census2010RaceStats, Census2010Households
from geo.views import get_censustract_geos
from geo.models import Geo
from hmda.views import loan_originations_as_json, base_hmda_query
from respondents.models import Institution

def assemble_stats(lar_data, tracts):
    """
    assembles a lender's applications by those made
    in low, medium and high minority areas;
    we might be assembling stats for a lender or peer;
    """
    lma_sum = 0
    mma_sum = 0
    hma_sum = 0
    for tract in tracts:
        tract_volume = 0
        stats = tract.census2010racestats
        if tract.geoid in lar_data.keys():
            tract_volume = lar_data[tract.geoid]['volume']
        if stats.non_hisp_white_only_perc:
            minority_pct = 1 - stats.non_hisp_white_only_perc
            if minority_pct < .5:
                lma_sum += tract_volume
            elif minority_pct < .8:
                mma_sum += tract_volume
            else:
                hma_sum += tract_volume
    lar_total = lma_sum + mma_sum + hma_sum
    if lar_total:
        lar_stats = {
                'lma': lma_sum, 
                'lma_pct': round(1.0 * lma_sum / lar_total, 3), 
                'mma': mma_sum,
                'mma_pct': round(1.0 * mma_sum / lar_total, 3),
                'hma': hma_sum,
                'hma_pct': round(1.0 * hma_sum / lar_total, 3),
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

def odds_ratio(target_pct, peer_pct):
    """
    intended to calculate a lender/peers odds ratio for minority lending,
    based on counts of loans in mostly minority areas vs mostly majority areas
    this algorithm has not been vetted, so its current use 
    is only for mocking data flow to tables
    """
    odds_ratio = 0.0
    if peer_pct > 0.0 and target_pct < 1.0 and peer_pct < 1.0:
        odds_ratio = (target_pct/(1-target_pct))/(peer_pct/(1-peer_pct))
    return round(odds_ratio, 3)

def minority_aggregation_as_json(request):
    """
    aggregates minority population ranges and LAR counts 
    for a lender in an MSA
    by tract, msa and county
    """
    lender = Institution.objects.get(institution_id=request.GET.get('lender'))
    metro = Geo.objects.get(geo_type=Geo.METRO_TYPE, geoid=request.GET.get('metro'))
    tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=request.GET.get('metro'))
    lar_data = loan_originations_as_json(request)
    lender_stats = assemble_stats(lar_data, tracts)

    peer_request = HttpRequest()
    peer_request.GET['lender'] = lender.institution_id
    peer_request.GET['metro']= metro.geoid
    peer_request.GET['peers'] = 'true'
    peer_request.GET['action_taken'] = '1,2,3,4,5'
    peer_lar_data = loan_originations_as_json(peer_request)
    odds_lender = {}
    peer_stats = assemble_stats(peer_lar_data, tracts)

    target_lma_pct = lender_stats['lma_pct']
    peer_lma_pct = peer_stats['lma_pct']

    target_mma_pct = lender_stats['mma_pct']
    peer_mma_pct = peer_stats['mma_pct']

    target_hma_pct = lender_stats['hma_pct']
    peer_hma_pct = peer_stats['hma_pct']

    odds_msa_lma = odds_ratio(target_lma_pct, peer_lma_pct)
    odds_msa_mma = odds_ratio(target_mma_pct, peer_mma_pct)
    odds_msa_hma = odds_ratio(target_hma_pct, peer_hma_pct)

    odds_lender = {
        'odds_msa_lma' : odds_msa_lma,
        'odds_msa_mma' : odds_msa_mma,
        'odds_msa_hma' : odds_msa_hma
    }

    county_ids = sorted(set([tract.geoid[:5] for tract in tracts]))
    county_stats = {county_id: {} for county_id in county_ids}
    county_peer_stats = {county_id: {} for county_id in county_ids}
    county_odds = {county_id: {} for county_id in county_ids}
    for county_id in county_ids:
        county_tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, state=county_id[:2], county=county_id[2:])
        county_stats[county_id] = assemble_stats(lar_data, county_tracts)
        county_peer_stats[county_id] = assemble_stats(peer_lar_data, county_tracts)
        
        target_lma_pct = county_stats[county_id]['lma_pct']
        peer_lma_pct = county_peer_stats[county_id]['lma_pct']

        target_mma_pct = county_stats[county_id]['mma_pct']
        peer_mma_pct = county_peer_stats[county_id]['mma_pct']

        target_hma_pct = county_stats[county_id]['hma_pct']
        peer_hma_pct = county_peer_stats[county_id]['hma_pct']

        odds_county_lma = odds_ratio(target_lma_pct, peer_lma_pct)
        odds_county_mma = odds_ratio(target_mma_pct, peer_mma_pct)
        odds_county_hma = odds_ratio(target_hma_pct, peer_hma_pct)

        county_odds[county_id]['lma_odds'] = odds_county_lma
        county_odds[county_id]['mma_odds'] = odds_county_mma
        county_odds[county_id]['hma_odds'] = odds_county_hma

    return {
        #'msa': msa_stats,
        'target_lender': lender_stats,
        'peers': peer_stats,
        'odds_msa': odds_lender,
        'counties': county_stats,
        'county_odds' : county_odds
        }

def race_summary(request):
    """Race summary statistics"""
    geos = get_censustract_geos(request)
    if geos is None:
        return HttpResponseBadRequest("Missing lat/lon or metro")
    query = Census2010RaceStats.objects.filter(geoid__in=geos)
    return query

def race_summary_as_json(request_dict):
    records = race_summary(request_dict)

    data = {}
    for stats in records:
        data[stats.geoid_id] = {
            'total_pop': stats.total_pop,
            'hispanic': stats.hispanic,
            'non_hisp_white_only': stats.non_hisp_white_only,
            'non_hisp_black_only': stats.non_hisp_black_only,
            'non_hisp_asian_only': stats.non_hisp_asian_only,
            'minority_perc': 1-stats.non_hisp_white_only_perc,
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
    tracts_in_msa = get_censustract_geos(request)
    queryset = Census2010RaceStats.objects.filter(geoid__in=tracts_in_msa)
    file_name = 'HMDA-Census-Tract_2013_Lender%s_MSA%s.csv' % (institution_id, metro)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    writer = csv.writer(response, csv.excel)
    #response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"geoid"),
        smart_str(u"Total Population"),
        smart_str(u"Hispanic Percentage"),
        smart_str(u"White Only Percentage"),
        smart_str(u"Non Hispanic Black Only Percentage"),
        smart_str(u"Non Hispanic Asian Only Percentage"),
        smart_str(u"HMDA LAR Count"),
        smart_str(u"Total Households"),
    ])
    for obj in queryset:
        geoid = "'%s'" % str(obj.geoid.geoid)
        lar_count = HMDARecord.objects.filter(institution_id=institution_id, geo=obj.geoid, action_taken__in=action_taken_selected).filter(base_hmda_query()).count()
        census_households = Census2010Households.objects.filter(geoid=obj.geoid).first()
        if census_households:
            num_households = census_households.total
        else:
            num_households = 0
        writer.writerow([
            smart_str(geoid),
            smart_str(obj.total_pop),
            smart_str(obj.hispanic_perc * 100),
            smart_str(obj.non_hisp_white_only_perc * 100),
            smart_str(obj.non_hisp_black_only_perc * 100),
            smart_str(obj.non_hisp_asian_only_perc * 100),
            smart_str(lar_count),
            smart_str(num_households),
        ])
    return response
