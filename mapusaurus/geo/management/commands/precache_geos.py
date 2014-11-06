import urllib

from django.core import urlresolvers
from django.core.management.base import BaseCommand

from geo.views import to_lat, to_lon


class Command(BaseCommand):
    """Precache all of the geojson tiles in the continental US. First argument
    indicates host, defaulting to 'http://localhost'. Optionally, split the
    workload across multiple process, e.g. by calling with host 0 5, host 1 5,
    host 2 5, host 3 5, host 4 5 separately"""
    args = "<host> <identifier> <out-of>"
    help = "Precache census tract and county shape tiles"

    urls = {
        'geo:topotiles': range(9, 13),
    }
    #   Roughly the bounds of the continental US
    min_lon = -125
    max_lon = -66
    min_lat = 26
    max_lat = 49

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
                handle = urllib.urlopen(self.host + url)
                handle.read()     # actually read the content

    def handle(self, *args, **options):
        """Main entry point"""
        if len(args) >= 1:
            self.host = args[0]
        else:
            self.host = 'http://localhost'

        if len(args) >= 3:
            identifier, max_processes = map(int, args[1:3])
        else:
            identifier, max_processes = 0, 1

        for name, zoom in ((name, zoom)
                           for name in Command.urls
                           for zoom in Command.urls[name]):
            self.per_zoom_level(name, zoom, identifier, max_processes)
