from urllib import urlencode

from django.shortcuts import render
from django.db.models.query import QuerySet
from geo.models import Geo
from hmda.models import LendingStats
from hmda.management.commands.calculate_loan_stats import (calculate_median_loans)
from respondents.models import Institution, LenderHierarchy

def map(request, template):
    """Display the map. If lender info is present, provide it to the
    template"""
    lender = request.GET.get('lender', '')
    metro = request.GET.get('metro')
    context = {}
    if lender and len(lender) > 1 and lender[0].isdigit():
        query = Institution.objects.filter(institution_id=lender)
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

    if lender and metro:
        hierarchy_list = LenderHierarchy.objects.filter(organization_id=lender.lenderhierarchy_set.get().organization_id).values_list('institution_id', flat=True)
        institution_hierarchy = Institution.objects.filter(institution_id__in=hierarchy_list).order_by('-assets')
        context['institution_hierarchy'] = institution_hierarchy 
        context['institution_peers'] = get_peer_list(lender, metro) 
        context['download_url'] = make_download_url(lender, metro)
        context['hierarchy_download_url'] = make_download_url(institution_hierarchy, metro)
    context['median_loans'] = lookup_median(lender, metro) or 0
    if context['median_loans']:
        # 50000 is an arbitrary constant; should be altered if we want to
        # change how big the median circle size is
        context['scaled_median_loans'] = 50000 / context['median_loans']
    else:
        context['scaled_median_loans'] = 0

    return render(request, template, context)

def get_peer_list(lender, metro):
    loan_stats = lender.lendingstats_set.get(geo_id=metro.geoid)    
    percent_50 = loan_stats.lar_count * .50
    percent_200 = loan_stats.lar_count * 2.0
    peer_list = LendingStats.objects.filter(geo_id=metro.geoid, fha_bucket=loan_stats.fha_bucket, lar_count__range=(percent_50, percent_200)).values_list('institution_id', flat=True)
    institution_peers = Institution.objects.filter(institution_id__in=peer_list).order_by('assets')
    return institution_peers

def make_download_url(lender, metro):
    """Create a link to CFPB's HMDA explorer, either linking to all of this
    lender's records, or to just those relevant for an MSA. MSA's are broken
    into divisions in that tool, so make sure the query uses the proper ids"""
    where = ""
    if lender:
        where = 'as_of_year=2013 AND property_type IN (1,2) AND lien_status=1 AND owner_occupancy=1 AND '
        count = 0 
        if type(lender) is QuerySet:
            for institution in lender:
                query = '(agency_code=%s AND respondent_id="%s")'
                where += query % (institution.agency_id, institution.respondent_id)
                count += 1
                if(count < len(lender)):
                    where += "OR"
        else:
            query = '(agency_code=%s AND respondent_id="%s")'
            where += query % (lender.agency_id, lender.respondent_id)
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
        lender_str = lender.institution_id
        if metro:
            stat = LendingStats.objects.filter(
                institution_id=lender_str, geo_id=metro.geoid).first()
            if stat:
                return stat.lar_median
        return calculate_median_loans(lender_str, metro)
