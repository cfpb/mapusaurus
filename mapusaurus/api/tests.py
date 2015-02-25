import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpRequest, HttpResponse, HttpResponseBadRequest

from django.test import TestCase
from mock import Mock, patch

from utils import use_GET_in, state_county_filter
from api.views import msa, msas, tables

class ConversionTest(TestCase):
    def test_use_GET_in(self):
        fn, request = Mock(), Mock()
        request.GET.lists.return_value = [('param1', [0]), ('param2', [-1])]

        # Dictionaries become JSON
        fn.return_value = {'a': 1, 'b': 2}
        response = use_GET_in(fn, request)
        self.assertEqual(json.loads(response.content), {'a': 1, 'b': 2})
        self.assertEqual(fn.call_args[0][0], {'param1': [0], 'param2': [-1]})

        # Everything else is unaltered
        fn.return_value = HttpResponseNotFound('Oh noes')
        response = use_GET_in(fn, request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'Oh noes')


class ViewsTests(TestCase):
    fixtures = ['agency.json', 'fake_msa.json', 'api_tracts.json', 'test_counties.json', 'fake_respondents.json']

    def test_api_all_user_errors(self):
        resp = self.client.get(reverse('all'))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('all'), {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'',
                                    'swLon':'-88.225583',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})

        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('all'),   {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'41.597775',
                                    'swLon':'',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        self.assertEqual(resp.status_code, 400)

    def test_api_msas_user_errors(self):
        resp = self.client.get(reverse('msas'))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('msas'), {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'',
                                    'swLon':'-88.225583',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})

        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('msas'),   {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'41.597775',
                                    'swLon':'',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        self.assertEqual(resp.status_code, 400)

    def test_api_msas_endpoint(self):
        """should return a list of MSA ids in view"""
        coords = {'neLat': '36.551569', 'neLon':'-78.961487', 'swLat':'35.824494', 'swLon':'-81.828918'}
        url = reverse(msas)
        resp = self.client.get(url, coords)
        result_list = json.loads(resp.content)
        self.assertTrue(isinstance(result_list, list))
        self.assertContains(resp, '49180')

    def test_api_msa_endpoint(self):
        """should return tract-level geojson for a lender/MSA pair"""
        params = {'lender': '90000451965', 'metro': '49180'}
        url = reverse(msa)
        resp = self.client.get(url, params)
        result_dict = json.loads(resp.content)
        self.assertTrue(isinstance(result_dict, dict))
        self.assertContains(resp, 'features')

    def test_api_tables_endpoint(self):
        """should return table_data json for a lender/MSA pair"""
        params = {'lender': '90000451965', 'metro': '49180'}
        url = reverse(tables)
        resp = self.client.get(url, params)
        result_dict = json.loads(resp.content)
        self.assertTrue(isinstance(result_dict, dict))
        keys = ['lender', 'peers', 'odds', 'msa', 'counties']
        lender_keys = ['hma_pct', 'lma_pct', 'mma_pct', 'lma', 'mma', 'hma', 'lar_total']
        for key in keys:
            self.assertTrue(key in result_dict['table_data'].keys())
        for key in lender_keys:
                self.assertTrue(key in result_dict['table_data']['lender'].keys())
        self.assertTrue(len(result_dict['table_data']['counties']) > 0)


