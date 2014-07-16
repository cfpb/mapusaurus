import itertools

from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, Polygon
from geo.models import Geo


class Command(BaseCommand):
    args = "<path/to/shapefile>"
    help = "Load the State shapefile from Census"

    def load_data(self, shapefile_name):
        ds = DataSource(shapefile_name)
        layer = ds[0]
        columns = [layer.get_fields(field_name) for field_name in
                   ('GEOID', 'NAME', 'STATEFP', 'COUNTYFP', 'TRACTCE',
                    'INTPTLAT', 'INTPTLON')]
        columns.append(layer.get_geoms(True))
        rows = itertools.izip(*columns)
        batch = []
        for geoid, name, state, county, tract, lat, lon, geom in rows:
            # Convert everything into multi polygons
            if isinstance(geom, Polygon):
                geom = MultiPolygon(geom)
            lons, lats = zip(*[pt for polygon in geom.coords
                               for line in polygon for pt in line])
            batch.append(Geo(
                geoid=geoid, geo_type=Geo.TRACT_TYPE, name=name, state=state,
                county=county, tract=tract, minlat=min(lats), maxlat=max(lats),
                minlon=min(lons), maxlon=max(lons), centlat=float(lat),
                centlon=float(lon), geom=geom))
            if len(batch) == 1000:
                Geo.objects.bulk_create(batch)
                batch = []
        Geo.objects.bulk_create(batch)      # last batch

    def handle(self, *args, **options):
        shapefile_name = args[0]
        self.load_data(shapefile_name)


# The 2010 census had a few errors that got fixed in later TIGER files.
# Unfortunately, both HMDA and census population statistics refer to the
# original, erroneous census tracts. See
# http://www.census.gov/geo/reference/pdfs/Geography_Notes.pdf
errors_in_2010 = {
    # Original -> Correct
    "04019002701": "04019002704",
    "04019002903": "04019002906",
    "04019410501": "04019004118",
    "04019410502": "04019004121",
    "04019410503": "04019004125",
    "04019470400": "04019005200",
    "04019470500": "04019005300",

    "06037930401": "06037137000",

    "36053940101": "36053030101",
    "36053940102": "36053030102",
    "36053940103": "36053030103",
    "36053940200": "36053030200",
    "36053940300": "36053030300",
    "36053940401": "36053030401",
    "36053940403": "36053030403",
    "36053940600": "36053030600",
    "36053940700": "36053030402",

    "36065940000": "36065024800",
    "36065940100": "36065024700",
    "36065940200": "36065024900",

    # This tract should never have existed; also zero population so no harm
    # removing it
    "36085008900": None,
}
