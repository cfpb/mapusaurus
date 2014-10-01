from urllib import urlencode

from django.shortcuts import render

from geo.models import Geo
from hmda.models import LendingStats
from respondants.models import Institution


def map(request):
    """Display the map. If lender info is present, provide it to the
    template"""
    lender = request.GET.get('lender', '')
    metro = request.GET.get('metro')
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

