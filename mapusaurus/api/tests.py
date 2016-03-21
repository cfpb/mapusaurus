import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound

from django.test import TestCase
from mock import Mock

from utils import use_GET_in
from api.views import msas, tables, tables_csv

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
        resp = self.client.get(reverse('all'), {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'',
                                    'swLon':'-88.225583',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(reverse('all'),   {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'41.597775',
                                    'swLon':'',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        self.assertEqual(resp.status_code, 404)


    def test_api_msas_user_errors(self):
        resp = self.client.get(reverse('msas'))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(reverse('msas'), {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'',
                                    'swLon':'-88.225583',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(reverse('msas'),   {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'41.597775',
                                    'swLon':'',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        self.assertEqual(resp.status_code, 404)

    def test_api_msas_endpoint(self):
        """should return a list of MSA ids in view"""
        coords = {'neLat': '36.551569', 'neLon':'-78.961487', 'swLat':'35.824494', 'swLon':'-81.828918', 'year':2013}
        url = reverse(msas)
        resp = self.client.get(url, coords)
        result_list = json.loads(resp.content)
        self.assertTrue(isinstance(result_list, list))
        # in the fake_msa.json fixture
        self.assertContains(resp, '49180')
        # don't find an MSA with the wrong year
        self.assertNotContains(resp, '49181')

    def test_api_tables_endpoint(self):
        """should return table_data json for a lender/MSA pair"""
        params = {'lender': '90000451965', 'metro': '49180', 'year':'2013'}
        url = reverse(tables)
        resp = self.client.get(url, params)
        result_dict = json.loads(resp.content)
        self.assertTrue(isinstance(result_dict, dict))
        keys = ['counties', 'msa']
        lender_keys = ['hma_pct', 'lma_pct', 'mma_pct', 'lma', 'mma', 'hma', 'lar_total', 'peer_hma_pct', 'peer_lma_pct', 'peer_mma_pct', 'peer_lma', 'peer_mma', 'peer_hma', 'peer_lar_total', 'odds_lma', 'odds_mma', 'odds_hma']
        for key in keys:
            self.assertTrue(key in result_dict.keys())
        for key in lender_keys:
            self.assertTrue(key in result_dict['msa'].keys())
        self.assertTrue(len(result_dict['msa']) > 0)

    def test_api_tables_csv(self):
        import csv, StringIO
        """should return table_data csv for a lender/MSA pair"""
        params = {'lender': '90000451965', 'metro': '49180', 'year': '2013'}
        url = reverse(tables_csv)
        resp = self.client.get(url, params)
        f = StringIO.StringIO(resp.content)
        result = csv.DictReader(f, delimiter=',')
        for result_dict in result:
            pass
        self.assertTrue(isinstance(result_dict, dict))
        input_keys = ['msa_or_county_id', 'peer_lar_total', 'name']
        lender_keys  = ['hma_pct', 'lma_pct', 'mma_pct', 'lma', 'mma', 'hma', 'lar_total', 
            'peer_hma_pct', 'peer_lma_pct', 'peer_mma_pct', 'peer_lma', 'peer_mma', 
            'peer_hma', 'peer_lar_total', 'odds_lma', 'odds_mma', 'odds_hma']
        keys = input_keys + lender_keys
        header_dict = { "msa_or_county_id":"MSA or County ID",
            "peer_lar_total":"Total LAR of Peers","name":"County Name",
            "hma_pct":"Pct in HMA","lma_pct":"Pct in LMA","mma_pct":"Pct in MMA",
            "lma":"LAR Count in LMA","mma":"LAR Count in MMA","hma":"LAR Count in HMA",
            "lar_total":"Total LAR in MSA","peer_hma_pct":"Odds Ratio in HMA",
            "peer_mma_pct":"Odds Ratio in MMA","peer_lma_pct":"Odds Ratio in LMA",
            "peer_lma":"Total Peer LAR in LMA","peer_mma":"Total Peer LAR in MMA",
            "peer_hma":"Total Peer LAR in HMA",
            "odds_lma":"Odds LMA","odds_mma":"Odds MMA","odds_hma":"Odds HMA"}
        for key in keys:
            self.assertTrue(header_dict[key] in result_dict.keys())
        self.assertTrue(len(result_dict[header_dict['msa_or_county_id']]) > 0)
