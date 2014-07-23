import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import patch

from geo.management.commands.precache_geos import Command as Precache


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
