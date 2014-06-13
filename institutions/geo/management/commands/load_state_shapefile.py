from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from geo.models import StateCensusTract, censustract_mapping


class Command(BaseCommand):
    args = "<path/to/shapefile>"
    help = "Load the State shapefile from Census"

    def load_data(self, shapefile_name):
        lm = LayerMapping(
            StateCensusTract, shapefile_name, censustract_mapping,
            transform=True, encoding='iso-8859-1')
        lm.save(strict=True, verbose=True)

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
