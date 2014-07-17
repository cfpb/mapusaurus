import itertools

from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, Polygon
from geo.models import Geo


class Command(BaseCommand):
    help = "Load shapes (tracts, counties, msas) from a shape file."
    args = "<path/to/shapefile>"

    def geo_type(self, row_dict):
        """Inspect the row to determine which type of geometry it represents"""
        if row_dict.get('TRACTCE'):
            return Geo.TRACT_TYPE
        if row_dict.get('COUNTYFP') and row_dict.get('STATEFP'):
            return Geo.COUNTY_TYPE
        if row_dict.get('LSAD') == 'M1':
            return Geo.METRO_TYPE
        if row_dict.get('LSAD') == 'M2':
            return Geo.MICRO_TYPE

    def handle(self, *args, **options):
        shapefile_name = args[0]
        ds = DataSource(shapefile_name, encoding='iso-8859-1')
        layer = ds[0]
        columns = [layer.get_fields(field) for field in layer.fields]
        columns.append(layer.get_geoms(True))
        rows = itertools.izip(*columns)
        batch, batch_count = [], 0
        for row in rows:
            row_dict = dict((field_name, row[idx])
                            for idx, field_name in enumerate(layer.fields))
            geom = row[-1]

            # Convert everything into multi polygons
            if isinstance(geom, Polygon):
                geom = MultiPolygon(geom)
            lons, lats = zip(*[pt for polygon in geom.coords
                               for line in polygon for pt in line])

            # Use ".get('field') or None" to convert empty strings into Nones
            batch.append(Geo(
                geoid=row_dict['GEOID'], geo_type=self.geo_type(row_dict),
                name=row_dict['NAME'], state=row_dict.get('STATEFP') or None,
                county=row_dict.get('COUNTYFP') or None,
                csa=row_dict.get('CSAFP') or None,
                cbsa=row_dict.get('CBSAFP') or None,
                minlat=min(lats), maxlat=max(lats), minlon=min(lons),
                maxlon=max(lons),
                centlat=float(row_dict['INTPTLAT']),
                centlon=float(row_dict['INTPTLON']),
                geom=geom))
            if len(batch) == 100:
                batch_count += 1
                self.stdout.write('Saving batch %d' % batch_count)
                Geo.objects.bulk_create(batch)
                batch = []
        Geo.objects.bulk_create(batch)      # last batch
