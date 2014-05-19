import sys

from django.core.management.base import BaseCommand, CommandError
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
