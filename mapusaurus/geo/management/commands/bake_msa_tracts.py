import os
import json
import datetime

from django.core.management.base import BaseCommand, CommandError
# from django.core.management.base import NoArgsCommand
from geo.models import Geo

tract_dir = '/var/www/static/tracts'

class Command(BaseCommand):
    help = """bake all metro tracts to local json files"""

    def handle(self, *args, **options):
        if not os.path.isdir(tract_dir):
            os.mkdir(tract_dir)
        now = datetime.datetime.now()
        counter = 0
        msas = Geo.objects.filter(geo_type=Geo.METRO_TYPE)
        for metro in msas:
            counter += 1
            filename = "%s/%s.json" % (tract_dir, metro.geoid)
            tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro.geoid)
            tractd = {}
            for tract in tracts:
                tractd[tract.geoid] = tract.geom.simplify(0.001).coords
            with open(filename, 'wb') as f:
                f.write(json.dumps(tractd))
            if counter > 1 and counter % 50 == 0:
                self.stdout.write("%s baked" % counter)
        self.stdout.write("took %s to bake %s metros to %s" % ( (datetime.datetime.now() - now), msas.count(), tract_dir ))
