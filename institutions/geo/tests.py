import json

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.test import TestCase
from mock import patch

from geo.management.commands.load_geos_from import Command as LoadGeos
from geo.management.commands.precache_geos import Command as Precache
from geo.models import Geo


class ViewTest(TestCase):
    fixtures = ['many_tracts', 'test_counties']

    def test_tract_tiles(self):
        # lat/lon roughly: 0 to 11
        resp = self.client.get(reverse(
            'geo:tract_tiles',
            kwargs={'zoom': 5, 'xtile': 16, 'ytile': 15}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']),
                         # Doesn't grab the negative tract
                         3)

        # lat/lon roughly: -6 to -3
        resp = self.client.get(reverse(
            'geo:tract_tiles',
            kwargs={'zoom': 7, 'xtile': 62, 'ytile': 65}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']), 1)

    def test_county_tiles(self):
        # lat/lon roughly: 0 to 5
        resp = self.client.get(reverse(
            'geo:county_tiles',
            kwargs={'zoom': 6, 'xtile': 32, 'ytile': 31}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']), 1)
        self.assertEqual(resp['features'][0]['properties']['name'],
                         'Positive County')

        # lat/lon roughly: -6 to -3
        resp = self.client.get(reverse(
            'geo:county_tiles',
            kwargs={'zoom': 7, 'xtile': 62, 'ytile': 65}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']), 1)
        self.assertEqual(resp['features'][0]['properties']['name'],
                         'Negative County')

        # lat/lon roughly: -3.1 to -2.8; Testing that the centroid is checked
        resp = self.client.get(reverse(
            'geo:county_tiles',
            kwargs={'zoom': 10, 'xtile': 503, 'ytile': 520}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']), 1)
        self.assertEqual(resp['features'][0]['properties']['name'],
                         'Negative County')


class PrecacheTest(TestCase):
    def setUp(self):
        self.original_urls = Precache.urls

    def tearDown(self):
        Precache.urls = self.original_urls

    @patch('geo.management.commands.precache_geos.Client')
    def test_handle_with_args(self, client):
        Precache.urls['geo:tract_tiles'] = range(3, 6)
        Precache.urls['geo:county_tiles'] = range(1, 5)
        Precache().handle('3', '5')
        self.assertEqual(4, client.return_value.get.call_count)
        args = [args[0][0] for args in client.return_value.get.call_args_list]
        tract_calls = set(filter(lambda s: 'tracts' in s, args))
        self.assertEqual(3, len(tract_calls))
        county_calls = set(filter(lambda s: 'counties' in s, args))
        self.assertEqual(1, len(county_calls))

    @patch('geo.management.commands.precache_geos.Client')
    def test_handle_no_args(self, client):
        Precache.urls['geo:tract_tiles'] = range(3, 6)
        Precache.urls['geo:county_tiles'] = range(1, 5)
        Precache().handle()
        self.assertEqual(28, client.return_value.get.call_count)
        args = [args[0][0] for args in client.return_value.get.call_args_list]
        tract_calls = set(filter(lambda s: 'tracts' in s, args))
        self.assertEqual(22, len(tract_calls))
        county_calls = set(filter(lambda s: 'counties' in s, args))
        self.assertEqual(6, len(county_calls))


class LoadGeosFromTest(TestCase):
    def test_census_tract(self):
        row = ('1122233333', 'Tract 33333', '11', '222', '33333', '-45',
               '45', Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))))
        field_names = ('GEOID', 'NAME', 'STATEFP', 'COUNTYFP', 'TRACTCE',
                       'INTPTLAT', 'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(row, field_names)

        self.assertEqual('1122233333', geo.geoid)
        self.assertEqual(Geo.TRACT_TYPE, geo.geo_type)
        self.assertEqual('Tract 33333', geo.name)
        self.assertEqual('11', geo.state)
        self.assertEqual('222', geo.county)
        self.assertEqual('33333', geo.tract)
        self.assertEqual(None, geo.csa)
        self.assertEqual(None, geo.cbsa)
        self.assertEqual((-1, 0), (geo.minlon, geo.maxlon))
        self.assertEqual((0, 2), (geo.minlat, geo.maxlat))
        self.assertEqual(-45, geo.centlat)
        self.assertEqual(45, geo.centlon)

    def test_county(self):
        poly1 = Polygon(((0, 0), (0, 2), (-1, 2), (0, 0)))
        poly2 = Polygon(((-4, -2), (-6, -1), (-2, -2), (-4, -2)))
        row = ('11222', 'Some County', '11', '222', '-45', '45',
               MultiPolygon(poly1, poly2))
        field_names = ('GEOID', 'NAME', 'STATEFP', 'COUNTYFP', 'INTPTLAT',
                       'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(row, field_names)

        self.assertEqual('11222', geo.geoid)
        self.assertEqual(Geo.COUNTY_TYPE, geo.geo_type)
        self.assertEqual('Some County', geo.name)
        self.assertEqual('11', geo.state)
        self.assertEqual('222', geo.county)
        self.assertEqual(None, geo.tract)
        self.assertEqual(None, geo.csa)
        self.assertEqual(None, geo.cbsa)
        self.assertEqual((-6, 0), (geo.minlon, geo.maxlon))
        self.assertEqual((-2, 2), (geo.minlat, geo.maxlat))
        self.assertEqual(-45, geo.centlat)
        self.assertEqual(45, geo.centlon)

    def test_metro(self):
        row = ('12345', 'Big City', '090', '12345', 'M1', '-45', '45',
               Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))))
        field_names = ('GEOID', 'NAME', 'CSAFP', 'CBSAFP', 'LSAD', 'INTPTLAT',
                       'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(row, field_names)

        self.assertEqual('12345', geo.geoid)
        self.assertEqual(Geo.METRO_TYPE, geo.geo_type)
        self.assertEqual('Big City', geo.name)
        self.assertEqual(None, geo.state)
        self.assertEqual(None, geo.county)
        self.assertEqual(None, geo.tract)
        self.assertEqual('090', geo.csa)
        self.assertEqual('12345', geo.cbsa)

    def test_micro(self):
        row = ('12345', 'Small Town', '', '12345', 'M2', '-45', '45',
               Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))))
        field_names = ('GEOID', 'NAME', 'CSAFP', 'CBSAFP', 'LSAD', 'INTPTLAT',
                       'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(row, field_names)

        self.assertEqual('12345', geo.geoid)
        self.assertEqual(Geo.MICRO_TYPE, geo.geo_type)
        self.assertEqual('Small Town', geo.name)
        self.assertEqual(None, geo.state)
        self.assertEqual(None, geo.county)
        self.assertEqual(None, geo.tract)
        self.assertEqual(None, geo.csa)
        self.assertEqual('12345', geo.cbsa)
