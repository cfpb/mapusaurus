import json
import csv
from django.utils.encoding import smart_str
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import Census2010RaceStats,Census2010Households
from geo.views import get_censustract_geos
from geo.models import Geo
from hmda.views import loan_originations_as_json
from respondents.models import Institution

def get_minority_area_stats(target_lar_data, peer_lar_data, tracts):
    lma_sum = 0
    mma_sum = 0
    hma_sum = 0

    peer_lma_sum = 0
    peer_mma_sum = 0
    peer_hma_sum = 0
    for tract in tracts:
        target_tract_volume = 0
        peer_tract_volume = 0
        racestats = tract.census2010racestats
        if tract.geoid in target_lar_data.keys():
            target_tract_volume = target_lar_data[tract.geoid]['volume']
        if tract.geoid in peer_lar_data.keys():
                peer_tract_volume = peer_lar_data[tract.geoid]['volume']
        if racestats.non_hisp_white_only_perc:
            minority_pct = 1 - racestats.non_hisp_white_only_perc
            if minority_pct < .5:
                lma_sum += target_tract_volume
                peer_lma_sum += peer_tract_volume
            elif minority_pct < .8:
                mma_sum += target_tract_volume
                peer_mma_sum += peer_tract_volume

            else:
                hma_sum += target_tract_volume
                peer_hma_sum += peer_tract_volume

    minority_area_stats = (lma_sum, mma_sum, hma_sum, peer_lma_sum, peer_mma_sum, peer_hma_sum)
    return minority_area_stats

def assemble_stats(lma_sum, mma_sum, hma_sum, peer_lma_sum, peer_mma_sum, peer_hma_sum):
    """
    assembles a lender's applications by those made
    in low, medium and high minority areas;
    we might be assembling stats for a lender or peer;
    """
    lma_pct = 0.0
    mma_pct = 0.0
    hma_pct = 0.0

    peer_lma_pct = 0.0
    peer_mma_pct = 0.0
    peer_hma_pct = 0.0

    stats = {}

    target_lar_total = lma_sum + mma_sum + hma_sum
    if target_lar_total:
        lma_pct = round(1.0 * lma_sum / target_lar_total, 3)
        mma_pct = round(1.0 * mma_sum / target_lar_total, 3)
        hma_pct = round(1.0 * hma_sum / target_lar_total, 3)
        maj_pct = round(mma_pct + hma_pct, 3)
        stats.update({
                'lma': lma_sum, 
                'lma_pct': lma_pct, 
                'mma': mma_sum,
                'mma_pct': mma_pct,
                'hma': hma_sum,
                'hma_pct': hma_pct,
                'maj_pct': maj_pct,
                'lar_total': target_lar_total
        })
    else:
        stats.update({
            'lar_total': 0,
            'lma': 0, 
            'lma_pct': 0, 
            'mma': 0,
            'mma_pct': 0,
            'hma': 0,
            'hma_pct': 0
        })
    #assemble peer data
    peer_lar_total = peer_lma_sum + peer_mma_sum + peer_hma_sum
    if peer_lar_total:
        peer_lma_pct = round(1.0 * peer_lma_sum / peer_lar_total, 3)
        peer_mma_pct = round(1.0 * peer_mma_sum / peer_lar_total, 3)
        peer_hma_pct = round(1.0 * peer_hma_sum / peer_lar_total, 3)
        peer_maj_pct = round(peer_mma_pct + peer_hma_pct, 3)
        stats.update({
                'peer_lma': peer_lma_sum, 
                'peer_lma_pct': peer_lma_pct, 
                'peer_mma': peer_mma_sum,
                'peer_mma_pct': peer_mma_pct,
                'peer_hma': peer_hma_sum,
                'peer_hma_pct': peer_hma_pct,
                'peer_maj_pct': peer_maj_pct,
                'peer_lar_total': peer_lar_total
        })
    else:
        stats.update({
            'peer_lma': 0,
            'peer_lma_pct': 0, 
            'peer_mma': 0, 
            'peer_mma_pct': 0,
            'peer_hma': 0,
            'peer_hma_pct': 0,
            'peer_lar_total': 0
        })
    odds_lma = odds_ratio(lma_pct, peer_lma_pct)
    odds_mma = odds_ratio(mma_pct, peer_mma_pct)
    odds_hma = odds_ratio(hma_pct, peer_hma_pct)
    odds_maj = odds_ratio(mma_pct+hma_pct, peer_mma_pct+peer_hma_pct)
    stats.update({
        'odds_lma':odds_lma,
        'odds_mma':odds_mma,
        'odds_hma':odds_hma,
        'odds_maj':odds_maj
    })
    return stats
    

def odds_ratio(target_pct, peer_pct):
    """
    intended to calculate a lender/peers odds ratio for minority lending,
    based on counts of loans in mostly minority areas vs mostly majority areas
    this algorithm has not been vetted, so its current use 
    is only for mocking data flow to tables
    """
    odds_ratio = 0.0
    if peer_pct == 0.0:
        return None
    elif target_pct == 0.0:
        odds_ratio = 0.0
    elif target_pct == peer_pct:
        odds_ratio = 1.0
    elif peer_pct > 0.0 and target_pct < 1.0 and peer_pct < 1.0:
        odds_ratio = (target_pct/(1-target_pct))/(peer_pct/(1-peer_pct))
    return round(odds_ratio, 3)

def minority_aggregation_as_json(request):
    """
    aggregates minority population ranges and LAR counts 
    for a lender in an MSA
    by tract, msa and county
    """
    msa_target_lma_sum = 0
    msa_target_mma_sum = 0
    msa_target_hma_sum = 0

    msa_peer_lma_sum = 0
    msa_peer_mma_sum = 0
    msa_peer_hma_sum = 0


    msa_stats = {}

    lar_data = loan_originations_as_json(request)
    lender = get_object_or_404(Institution, pk=request.GET.get('lender'))
    metro = get_object_or_404(Geo, geo_type=Geo.METRO_TYPE, geoid=request.GET.get('metro'))
    peer_request = HttpRequest()
    peer_request.GET['lender'] = lender.institution_id
    peer_request.GET['metro']= metro.geoid
    peer_request.GET['peers'] = 'true'
    peer_lar_data = loan_originations_as_json(peer_request)

    msa_counties = Geo.objects.filter(geo_type=Geo.COUNTY_TYPE, cbsa=metro.cbsa, year=metro.year)
    county_stats = {}
    for county in msa_counties:
        county_tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, state=county.state, county=county.county, year=metro.year)
        minority_area_stats = get_minority_area_stats(lar_data, peer_lar_data, county_tracts)
        county_stats[county.geoid] = assemble_stats(*minority_area_stats)
        county_stats[county.geoid]['name'] = county.name
        #tally target msa counts
        msa_target_lma_sum += county_stats[county.geoid]['lma']
        msa_target_mma_sum += county_stats[county.geoid]['mma']
        msa_target_hma_sum += county_stats[county.geoid]['hma']
        #tally peer msa counts
        msa_peer_lma_sum += county_stats[county.geoid]['peer_lma']
        msa_peer_mma_sum += county_stats[county.geoid]['peer_mma']
        msa_peer_hma_sum += county_stats[county.geoid]['peer_hma']
    #msa
    msa_minority_area_stats = (msa_target_lma_sum, msa_target_mma_sum, msa_target_hma_sum, msa_peer_lma_sum, msa_peer_mma_sum, msa_peer_hma_sum)
    msa_stats = assemble_stats(*msa_minority_area_stats)
    
    return {
        'msa': msa_stats,
        'counties': county_stats,
    }

def race_summary(request):
    """Race summary statistics"""
    geos = get_censustract_geos(request)
    if len(geos) > 0:
        query = Census2010RaceStats.objects.filter(geoid__in=geos)
    else:
        query = Census2010RaceStats.objects.all()
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
    year = request.GET.get('year')
    if institution_id and metro: 
        lar_data = loan_originations_as_json(request)
        tracts_in_msa = get_censustract_geos(request)
        queryset = Census2010RaceStats.objects.filter(geoid__in=tracts_in_msa)
        file_name = 'HMDA-Census-Tract_Year%s_Lender%s_MSA%s.csv' % (year, institution_id, metro)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        writer = csv.writer(response, csv.excel)
        writer.writerow([
            smart_str(u"geoid"),
            smart_str(u"Total Population"),
            smart_str(u"Hispanic Percentage"),
            smart_str(u"White Only Percentage"),
            smart_str(u"Non Hispanic Black Only Percentage"),
            smart_str(u"Non Hispanic Asian Only Percentage"),
            smart_str(u"Originated Loans"),
            smart_str(u"Total Households"),
        ])
        for obj in queryset:
            geoid = "'%s'" % str(obj.geoid.geoid)
            if lar_data.get(obj.geoid.geoid,None):
                lar_count = lar_data[obj.geoid.geoid]['volume']
                num_households = lar_data[obj.geoid.geoid]['num_households']
            else:
                lar_count = 0
                # if there's no loan data we can still get household data
                num_households = get_object_or_404(Census2010Households, geoid_id=obj.geoid.geoid).total
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
    else: 
        raise Http404("Invalid Institution or Metro")

