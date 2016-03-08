from urllib import urlencode

from django.shortcuts import render
from django.db.models.query import QuerySet
from geo.models import Geo
from hmda.models import LendingStats, Year
from hmda.management.commands.calculate_loan_stats import (calculate_median_loans)
from respondents.models import Institution

def map(request, template):
    """Display the map. If lender info is present, provide it to the
    template"""
    lender_selected = request.GET.get('lender', '')
    metro_selected = request.GET.get('metro')
    year_selected = int(request.GET.get('year',str(Year.objects.latest().hmda_year)))
    context = {}
    lender = Institution.objects.filter(institution_id=lender_selected).select_related('agency', 'zip_code', 'lenderhierarchy').first()
    metro = Geo.objects.filter(geo_type=Geo.METRO_TYPE,geoid=metro_selected).first()
    
    if lender:
        context['lender'] = lender
        hierarchy_list = lender.get_lender_hierarchy(True, True, year_selected)
        context['institution_hierarchy'] = hierarchy_list 
    if metro:
        context['metro'] = metro
    context['year'] = year_selected
    if lender and metro:
        peer_list = lender.get_peer_list(metro, True, True) 
        context['institution_peers'] = peer_list
        context['download_url'] = make_download_url(lender, metro)
        context['hierarchy_download_url'] = make_download_url(hierarchy_list, metro)
        context['peer_download_url'] = make_download_url(peer_list, metro)
        context['median_loans'] = lookup_median(lender, metro) or 0
        if context['median_loans']:
            # 50000 is an arbitrary constant; should be altered if we want to
            # change how big the median circle size is
            context['scaled_median_loans'] = 50000 / context['median_loans']
        else:
            context['scaled_median_loans'] = 0
    return render(request, template, context)

def make_download_url(lender, metro):
    """Create a link to CFPB's HMDA explorer, either linking to all of this
    lender's records, or to just those relevant for an MSA. MSA's are broken
    into divisions in that tool, so make sure the query uses the proper ids"""
    where = ""
    if lender:
        where = ''
        count = 0
        if type(lender) is QuerySet:
            for item in lender:
                query = '(agency_code=%s AND respondent_id="%s" AND year=%s)'
                where += query % (item.institution.agency_id, item.institution.respondent_id, item.institution.year)
                count += 1
                if(count < len(lender)):
                    where += "OR"
        else:
            query = '(agency_code=%s AND respondent_id="%s" AND as_of_year=%s)'
            where += query % (lender.agency_id, lender.respondent_id, lender.year)
    if metro:
        divisions = [div.metdiv for div in
                     Geo.objects.filter(
                         geo_type=Geo.METDIV_TYPE, cbsa=metro.cbsa, year=metro.year
                     ).order_by('cbsa')]
        if divisions:
            where += ' AND msamd IN ("' + '","'.join(divisions) + '")'
        else:   # no divisions, so just use the MSA
            where += ' AND msamd="' + metro.cbsa + '"'

    query = urlencode({
        '$where': where,
        '$limit': 0
    })
    base_url = 'https://api.consumerfinance.gov/data/hmda/slice/'
    return base_url + 'hmda_lar.csv?' + query

def lookup_median(lender, metro):
    """Look up median. If not present, calculate it."""
    if lender:
        lender_str = lender.institution_id
        if metro:
            stat = LendingStats.objects.filter(
                institution_id=lender_str, geo_id=metro.geoid).first()
            if stat:
                return stat.lar_median
        return calculate_median_loans(lender_str, metro)
