import itertools

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from geo.models import Geo


class Command(BaseCommand):
    help = "Load shapes (tracts, counties, msas) from a shape file."
    args = "<year> <path/to/shapefile>"

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
        if row_dict.get('LSAD') == 'M3':
            return Geo.METDIV_TYPE

    def process_row(self, year, row, field_names):
        """Runs for every shape in the shape file. Returns a kw-dict which
        will be passed to Geo"""
        row_dict = dict((field_name, row[idx])
                        for idx, field_name in enumerate(field_names))
        geom = row[-1]

        # Convert everything into multi polygons
        if isinstance(geom, Polygon):
            geom = MultiPolygon(geom)
        lons, lats = zip(*[pt for polygon in geom.coords
                           for line in polygon for pt in line])

        # Use ".get('field') or None" to convert empty strings into Nones
        return {
            'geoid': year+row_dict['GEOID'], 'geo_type': self.geo_type(row_dict),
            'name': row_dict['NAME'], 'state': row_dict.get('STATEFP') or None,
            'county': row_dict.get('COUNTYFP') or None,
            'tract': row_dict.get('TRACTCE') or None,
            'csa': row_dict.get('CSAFP') or None,
            'cbsa': row_dict.get('CBSAFP') or None,
            'metdiv': row_dict.get('METDIVFP') or None,
            'minlat': min(lats), 'maxlat': max(lats), 'minlon': min(lons),
            'maxlon': max(lons),
            'centlat': float(row_dict['INTPTLAT']),
            'centlon': float(row_dict['INTPTLON']),
            'geom': geom, 
            'year': year}

    def save_batch(self, batch):
        """We don't want to break any FKs, so we will only update geos if they
        already exist"""
        existing = set()
        for geoid_list in Geo.objects.values_list('geoid').filter(
                geoid__in=[kws['geoid'] for kws in batch]).iterator():
            existing.add(geoid_list[0])

        bulk_create = []
        for kws in batch:
            if kws['geoid'] in existing:
                Geo.objects.filter(geoid=kws['geoid']).update(**kws)
            else:
                bulk_create.append(Geo(**kws))
        if bulk_create:
            Geo.objects.bulk_create(bulk_create)

    def handle(self, *args, **options):
        old_debug = settings.DEBUG
        settings.DEBUG = False
        year = args[0]
        shapefile_name = args[1]
        ds = DataSource(shapefile_name, encoding='iso-8859-1')
        layer = ds[0]
        columns = [layer.get_fields(field) for field in layer.fields]
        columns.append(layer.get_geoms(True))
        rows = itertools.izip(*columns)
        batch, batch_count = [], 0
        for row in rows:
            batch.append(self.process_row(year, row, layer.fields))
            if len(batch) == 100:
                batch_count += 1
                self.stdout.write('Saving batch %d' % batch_count)
                self.save_batch(batch)
                batch = []
        self.save_batch(batch)  # last batch
        settings.DEBUG = old_debug
