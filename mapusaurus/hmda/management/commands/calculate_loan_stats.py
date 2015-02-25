from django.core.management.base import BaseCommand
from django.db import connection

from geo.models import Geo
from hmda.models import HMDARecord, LendingStats

class Command(BaseCommand):
    help = "Generate loans stats per lender, metro combination"

    def handle(self, *args, **kwargs):
        #   Remove existing stats; we're going to regenerate them
        LendingStats.objects.all().delete()
        lender_q = HMDARecord.objects.values_list('institution_id', flat=True).distinct('institution')
        for metro in Geo.objects.filter(
                geo_type=Geo.METRO_TYPE).order_by('name'):
            self.stdout.write("Processing " + metro.name)
            query = lender_q.filter(geo__cbsa=metro.geoid)
            for lender_str in query.iterator():
                median = calculate_median_loans(lender_str, metro) or 0
                lar = calculate_lar_count(lender_str, metro)
                fha = calculate_fha_count(lender_str, metro)
                fha_percentage = fha/float(lar) 
                if fha_percentage == 0:
                    bucket = 0 
                elif fha_percentage > 0 and fha_percentage <= .1:
                    bucket = 1 
                elif fha_percentage > .10 and fha_percentage <= .3:
                    bucket = 2 
                elif fha_percentage > .3 and fha_percentage <= .5:
                    bucket = 3
                elif fha_percentage > .5 and fha_percentage <= .7:
                    bucket = 4
                elif fha_percentage > .7:
                    bucket =5
 
                LendingStats.objects.create(
                    institution_id=lender_str, geo=metro, lar_median=median, lar_count=lar, fha_count=fha, fha_bucket=bucket)

def lar_query(lender_str, metro):
    lar_query = HMDARecord.objects.filter(institution_id=lender_str, geo__cbsa=metro.geoid, geo__geo_type=Geo.TRACT_TYPE)
    return lar_query

def calculate_lar_count(lender_str, metro):
    lar = lar_query(lender_str, metro)
    return lar.count()

def calculate_fha_count(lender_str, metro):
    lar = lar_query(lender_str, metro)
    return lar.filter(loan_type=2).count()

def calculate_median_loans(lender_str, metro):
    """For a given lender, find the median loans per census tract. Limit to
    metro if present. The ORM makes these aggregations ugly, so we use raw
    SQL."""
    # First, count how many tracts this lender operates in
    query = Geo.objects.filter(
        geo_type=Geo.TRACT_TYPE, hmdarecord__institution_id=lender_str)
    if metro:
        query = query.filter(cbsa=metro.geoid)
    num_tracts = query.values('geoid').distinct('geoid').count()

    cursor = connection.cursor()
    # Next, aggregate the # of loans per tract. This query will *not*
    # include zeros
    query = """
        SELECT COUNT(hmda_hmdarecord.id) AS loan_count
        FROM geo_geo LEFT JOIN hmda_hmdarecord ON (geoid=geo_id)
        WHERE geo_type = %s
        AND institution_id = %s
    """
    params = [Geo.TRACT_TYPE, lender_str]
    if metro:
        query = query + "AND cbsa = %s\n"
        params.append(metro.geoid)
    query += """
        GROUP BY geo_geo.geoid
        ORDER BY loan_count
        LIMIT 1
        OFFSET %s
    """
    params.append(num_tracts // 2)     # median
    cursor.execute(query, params)
    result = cursor.fetchone()
    if result:
        return result[0]
    
