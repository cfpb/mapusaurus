"""
tests of the helper functions for assembling tables for map page
"""
import json

from django.http import HttpRequest
from django.test import TestCase
# from mock import Mock, patch
from censusdata.views import minority_aggregation_as_json, sum_lar_tuples, assemble_stats, tally_msa_minority_stats, combine_peer_stats, odds_ratio
from hmda.views import loan_originations_as_json
from respondents.models import Institution
from geo.models import Geo

params = {'lender': '90000451965', 'metro': '49180'}
request = HttpRequest()
for param in params:
    request.GET[param]=params[param]

class ViewsUtilitiesTests(TestCase):
    fixtures = ['agency.json', 'fake_msa.json', 'api_tracts.json', 'test_counties.json', 'fake_respondents.json']

    def test_minority_aggregation_as_json(self):
        """should return a dict of 5 dicts returning minority values"""
        keys = ['lender', 'peers', 'odds', 'msa', 'counties']
        lender_keys = ['hma_pct', 'lma_pct', 'mma_pct', 'lma', 'mma', 'hma', 'lar_total']
        result_dict = minority_aggregation_as_json(request)
        self.assertTrue(isinstance(result_dict, dict))
        for key in keys:
            self.assertTrue(key in result_dict.keys())
        for key in lender_keys:
                self.assertTrue(key in result_dict['lender'].keys())
        self.assertTrue(len(result_dict['counties']) > 0)
        self.assertEqual(result_dict['lender']['lar_total'], 7)
        self.assertEqual(result_dict['peers']['lar_total'], 7)
        self.assertEqual(result_dict['odds'], None)
        self.assertEqual(result_dict['msa']['minority_pct'], 0.303)
        self.assertEqual(result_dict['counties']['11222']['lma'], 7)
        self.assertEqual(result_dict['counties']['11222']['lar_total'], 7)

    def test_sum_lar_tuples(self):
        """should return a sum of values drawn from a list of tuples"""
        mock_tups = [('tract', 7), ('tract', 8), ('tract', 9), ('tract', 100)]
        self.assertEqual(sum_lar_tuples(mock_tups), 124)

    def test_assemble_stats(self):
        """should calculate and return a dict of lender loan totals by minority area"""
        lar_data = loan_originations_as_json(request)
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=request.GET.get('metro'))
        lender_stats = assemble_stats(lar_data, tracts)
        self.assertEqual(lender_stats['hma_pct'], 0)
        self.assertEqual(lender_stats['lma_pct'], 1)
        self.assertEqual(lender_stats['mma_pct'], 0)
        self.assertEqual(lender_stats['lma'], 7)
        self.assertEqual(lender_stats['mma'], 0)
        self.assertEqual(lender_stats['hma'], 0)
        self.assertEqual(lender_stats['lar_total'], 7)

    def test_tally_msa_minority_stats(self):
        """should return a dict of minority stats for an MSA"""
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=request.GET.get('metro'))
        msa_pop, msa_minority_ct, msa_minority_pct = tally_msa_minority_stats(tracts)
        self.assertEqual(msa_pop, 14754)
        self.assertEqual(msa_minority_ct, 4476)
        self.assertEqual(msa_minority_pct, 0.303)

    def test_combine_peer_stats(self):
        """should return a dict collated minority stats for a group of lender peers"""
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=request.GET.get('metro'))
        metro = Geo.objects.get(geo_type=Geo.METRO_TYPE, geoid=request.GET.get('metro'))
        lender = Institution.objects.get(institution_id=request.GET.get('lender'))
        peers = lender.get_peer_list(metro, None, None)
        peer_data_collector = []
        for peer in peers:
            peer_request = HttpRequest()
            peer_request.GET['lender'] = peer.institution.institution_id
            peer_request.GET['metro']= metro.geoid
            peer_lar_data = loan_originations_as_json(peer_request)
            peer_data_collector.append(assemble_stats(peer_lar_data, tracts))
        peer_stats = combine_peer_stats(peer_data_collector)
        self.assertEqual(peer_stats['hma_pct'], 0.0)
        self.assertEqual(peer_stats['lma_pct'], 1.0)
        self.assertEqual(peer_stats['mma_pct'], 0.0)
        self.assertEqual(peer_stats['lma'], 7)
        self.assertEqual(peer_stats['mma'], 0)
        self.assertEqual(peer_stats['hma'], 0)
        self.assertEqual(peer_stats['lar_total'], 7)

    def test_odds_ratio(self):
        """
        should return demical representing the odds ratio
        for a lender/MSA pair compared with the lender's peers
        """
        odds1 = odds_ratio(1, 1, 0, 1)# should bail on division by zero and return None
        odds2 = odds_ratio(3, 100, 50, 50)
        odds3 = odds_ratio(3, 30, 50, 50)
        odds4 = odds_ratio(50, 50, 50, 50)
        odds5 = odds_ratio(50, 50, 5, 50)
        self.assertEqual(odds1, None)
        self.assertEqual(odds2, 0.0)
        self.assertEqual(odds3, 0.1)
        self.assertEqual(odds4, 1.0)
        self.assertEqual(odds5, 10.0)




