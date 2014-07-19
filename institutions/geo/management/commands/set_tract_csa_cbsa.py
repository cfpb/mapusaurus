from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = """Set the CSA and CBSA of census tracts to that of their
              associated counties"""

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE geo_geo
            SET cbsa = (SELECT cbsa FROM geo_geo county
                        WHERE county.geo_type = 2
                        AND county.state = geo_geo.state
                        AND county.county = geo_geo.county)
            WHERE geo_type = 3;
        """)
        cursor.execute("""
            UPDATE geo_geo
            SET csa = (SELECT csa FROM geo_geo county
                        WHERE county.geo_type = 2
                        AND county.state = geo_geo.state
                        AND county.county = geo_geo.county)
            WHERE geo_type = 3;
        """)
        cursor.close()
