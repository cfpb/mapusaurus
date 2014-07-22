import itertools

from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, Polygon
from geo.models import Geo


class Command(BaseCommand):
    args = "<path/to/shapefile>"
    help = "Load a county shapefile (i.e. the shapes of counties)"

    def load_data(self, shapefile_name):
        ds = DataSource(shapefile_name, encoding='iso-8859-1')
        layer = ds[0]
        columns = [layer.get_fields(field_name) for field_name in
                   ('GEOID', 'NAME', 'STATEFP', 'COUNTYFP', 'INTPTLAT',
                    'INTPTLON')]
        columns.append(layer.get_geoms(True))
        rows = itertools.izip(*columns)
        batch, batch_count = [], 0
        for geoid, name, state, county, lat, lon, geom in rows:
            # Convert everything into multi polygons
            if isinstance(geom, Polygon):
                geom = MultiPolygon(geom)
            lons, lats = zip(*[pt for polygon in geom.coords
                               for line in polygon for pt in line])
            batch.append(Geo(
                geoid=geoid, geo_type=Geo.COUNTY_TYPE, name=name, state=state,
                county=county, minlat=min(lats), maxlat=max(lats),
                minlon=min(lons), maxlon=max(lons), centlat=float(lat),
                centlon=float(lon), geom=geom))
            if len(batch) == 100:
                batch_count += 1
                self.stdout.write('Saving batch %d' % batch_count)
                Geo.objects.bulk_create(batch)
                batch = []
        Geo.objects.bulk_create(batch)      # last batch

    def handle(self, *args, **options):
        shapefile_name = args[0]
        self.load_data(shapefile_name)
