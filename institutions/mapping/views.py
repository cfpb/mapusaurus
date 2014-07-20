from django.shortcuts import render

from geo.models import Geo
from respondants.models import Institution


DOWNLOAD_URL = "http://www.consumerfinance.gov/hmda/explore#!/as_of_year=2012"
DOWNLOAD_URL += "&respondent_id=%s&agency_code=%s"


def home(request):
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

    return render(request, 'index.html', context)


def make_download_url(lender, metro):
    """Create a link to CFPB's HMDA explorer, either linking to all of this
    lender's records, or to just those relevant for an MSA. MSA's are broken
    into divisions in that tool, so make sure the query uses the proper ids"""
    if lender:
        download_url = DOWNLOAD_URL % (lender.ffiec_id,
                                       str(lender.agency_id))
        if metro:
            divisions = [div.metdiv for div in
                         Geo.objects.filter(
                             geo_type=Geo.METDIV_TYPE, cbsa=metro.geoid
                         ).order_by('geoid')]
            # convert into msamd-1, msamd-2, etc. key-value strings
            divisions = ['msamd-' + str(idx + 1) + '=' + div
                         for idx, div in enumerate(divisions)]
            if divisions:
                download_url += '&' + '&'.join(divisions)
            else:   # no divisions, so just use the MSA
                download_url += '&msamd-1=' + metro.geoid

        return download_url
