import json

from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest

from hmda.models import HMDARecord
from .models import Census2010RaceStats
from geo.views import get_censustract_geoids
from geo.models import Geo
from djqscsv import render_to_csv_response

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
        data[stats.geoid_id] = {
            'total_pop': stats.total_pop,
            'hispanic': stats.hispanic,
            'non_hisp_white_only': stats.non_hisp_white_only,
            'non_hisp_black_only': stats.non_hisp_black_only,
            'non_hisp_asian_only': stats.non_hisp_asian_only,
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
    tracts_in_msa = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro).values_list('geoid', flat=True)
    query = HMDARecord.objects.filter(institution_id=institution_id, geo_id__in=tracts_in_msa).values('geo_id', 'geo__census2010households__total', 'geo__census2010racestats__total_pop', 'geo__census2010racestats__hispanic_perc', 'geo__census2010racestats__non_hisp_white_only_perc', 'geo__census2010racestats__non_hisp_black_only_perc', 'geo__census2010racestats__non_hisp_asian_only_perc').annotate(volume=Count('geo_id'))
    return render_to_csv_response(query)
