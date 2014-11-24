from django.core.management.base import BaseCommand
from django.db import connection

from geo.models import Geo
from hmda.models import HMDARecord, LendingStats


class Command(BaseCommand):
    help = "Generate loans stats per lender, metro combination"

    def handle(self, *args, **kwargs):
        #   Remove existing stats; we're going to regenerate them
        count = LendingStats.objects.count()
        print "LendingStats Recordcount: "  + str(count)
        LendingStats.objects.all().delete()
        count = LendingStats.objects.count()
        print "LendingStats After Delete: "  + str(count)

        lender_q = HMDARecord.objects.values_list('lender').distinct('lender')

        print "# of Distinct Lenders:" +str(len(lender_q))

        for metro in Geo.objects.filter(
                geo_type=Geo.METRO_TYPE).order_by('name'):
            self.stdout.write("Processing " + metro.name)
            query = lender_q.filter(geoid__cbsa=metro.geoid)
            print "Lender_Q based on geoid: " + str(query.count())
            for lender_str in (h[0] for h in query.iterator()):
                median = calculate_median_loans(lender_str, metro) or 0
                print "median:" + str(median)
                LendingStats.objects.create(lender=lender_str, geoid=metro, median_per_tract=median)

            count = LendingStats.objects.count()
            print "LendingStats Recordcount: "  + str(count)




def calculate_median_loans(lender_str, metro):
    """For a given lender, find the median loans per census tract. Limit to
    metro if present. The ORM makes these aggregations ugly, so we use raw
    SQL."""
    # First, count how many tracts this lender operates in
    query = Geo.objects.filter(
        geo_type=Geo.TRACT_TYPE, hmdarecord__lender=lender_str)
    if metro:
        query = query.filter(cbsa=metro.geoid)
    num_tracts = query.values('geoid').distinct('geoid').count()
    print "num_tracts: " + str(num_tracts)

    cursor = connection.cursor()
    # Next, aggregate the # of loans per tract. This query will *not*
    # include zeros
    query = """
        SELECT COUNT(hmda_hmdarecord.id) AS loan_count
        FROM geo_geo LEFT JOIN hmda_hmdarecord ON (geoid=geoid_id)
        WHERE geo_type = %s
        AND lender = %s
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
