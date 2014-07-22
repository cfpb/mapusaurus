from django.core import urlresolvers
from django.core.management.base import BaseCommand
from django.test import Client

from geo.views import to_lat, to_lon


class Command(BaseCommand):
    """Precache all of the geojson tiles in the continental US. Optionally,
    split the workload across multiple process, e.g. by calling with 0 5, 1 5,
    2 5, 3 5, 4 5 separately"""
    args = "<identifier> <out-of>"
    help = "Precache census tract and county shape tiles"

    urls = {
        'geo:topotiles': range(9, 13),
    }
    #   Roughly the bounds of the continental US
    min_lat = -125
    max_lat = -66
    min_lon = 26
    max_lon = 49

    def per_zoom_level(self, url_name, zoom, identifier, max_procs):
        """Iterates through x and y tiles, hitting the ones we care about"""
        for xtile, ytile in ((x, y)
                             for x in range(2**zoom)
                             for y in range(2**zoom)
                             if y % max_procs == identifier):
            lat, lon = to_lat(zoom, ytile), to_lon(zoom, xtile)
            if (Command.min_lat < lat and lat < Command.max_lat
                    and Command.min_lon < lon and lon < Command.max_lon):
                url = urlresolvers.reverse(
                    url_name, kwargs={'zoom': zoom, 'xtile': xtile,
                                      'ytile': ytile})
                Client().get(url)

    def handle(self, *args, **options):
        """Main entry point"""
        if len(args) >= 2:
            identifier, max_processes = map(int, args[:2])
        else:
            identifier, max_processes = 0, 1

        for name, zoom in ((name, zoom)
                           for name in Command.urls
                           for zoom in Command.urls[name]):
            self.per_zoom_level(name, zoom, identifier, max_processes)
