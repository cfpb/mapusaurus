from django.core.management.base import BaseCommand
from django.db import connection

from geo.models import Geo


class Command(BaseCommand):
    help = """Set the CSA and CBSA of census tracts to that of their
              associated counties"""

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE geo_geo
            SET cbsa = (SELECT cbsa FROM geo_geo county
                        WHERE county.geo_type = %s
                        AND county.state = geo_geo.state
                        AND county.county = geo_geo.county
                        AND county.year = geo_geo.year)
            WHERE geo_type = %s;
        """, (Geo.COUNTY_TYPE, Geo.TRACT_TYPE))
        cursor.execute("""
            UPDATE geo_geo
            SET csa = (SELECT csa FROM geo_geo county
                        WHERE county.geo_type = %s
                        AND county.state = geo_geo.state
                        AND county.county = geo_geo.county
                        AND county.year = geo_geo.year)
            WHERE geo_type = %s;
        """, (Geo.COUNTY_TYPE, Geo.TRACT_TYPE))
        cursor.close()
