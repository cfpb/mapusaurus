from urllib import urlencode

from django.shortcuts import render

from geo.models import Geo
from hmda.models import LendingStats
from hmda.management.commands.calculate_loan_stats import (calculate_median_loans)
from respondants.models import Institution


def map(request):
    """Display the map. If lender info is present, provide it to the
    template"""
    lender = request.GET.get('lender', '')
    metro = request.GET.get('metro')
    template = request.GET.get('template', 'leaflet')
    context = {}
    if lender and len(lender) > 1 and lender[0].isdigit():
        query = Institution.objects.filter(agency_id=int(lender[0]))
        query = query.filter(ffiec_id=lender[1:])
        query = query.select_related('agency', 'zip_code')
        lender = query.first()
        if lender:
            context['lender'] = lender
    else:
        lender = None
    if metro:
        query = Geo.objects.filter(geo_type=Geo.METRO_TYPE,
                                   geoid=metro)
        metro = query.first()
        if metro:
            context['metro'] = metro
    context['download_url'] = make_download_url(lender, metro)
    context['median_loans'] = lookup_median(lender, metro) or 0
    if context['median_loans']:
        # 50000 is an arbitrary constant; should be altered if we want to
        # change how big the median circle size is
        context['scaled_median_loans'] = 50000 / context['median_loans']
    else:
        context['scaled_median_loans'] = 0

    if template == 'mapbox':
        return render(request, 'mapbox.html', context)
    else:
        return render(request, 'map.html', context)

def make_download_url(lender, metro):
    """Create a link to CFPB's HMDA explorer, either linking to all of this
    lender's records, or to just those relevant for an MSA. MSA's are broken
    into divisions in that tool, so make sure the query uses the proper ids"""
    if lender:
        where = 'as_of_year=2012 AND agency_code=%d AND respondent_id="%s"'
        where = where % (lender.agency_id, lender.ffiec_id)
        if metro:
            divisions = [div.metdiv for div in
                         Geo.objects.filter(
                             geo_type=Geo.METDIV_TYPE, cbsa=metro.geoid
                         ).order_by('geoid')]
            if divisions:
                where += ' AND msamd IN ("' + '","'.join(divisions) + '")'
            else:   # no divisions, so just use the MSA
                where += ' AND msamd="' + metro.geoid + '"'

        query = urlencode({
            '$where': where,
            '$limit': 0
        })
        base_url = 'https://api.consumerfinance.gov/data/hmda/slice/'
        return base_url + 'hmda_lar.csv?' + query

def lookup_median(lender, metro):
    """Look up median. If not present, calculate it."""
    if lender:
        lender_str = str(lender.agency_id) + lender.ffiec_id
        if metro:
            stat = LendingStats.objects.filter(
                lender=lender_str, geoid=metro.geoid).first()
            if stat:
                return stat.median_per_tract
        return calculate_median_loans(lender_str, metro)
