"""
tests of the helper functions for assembling tables for map page
"""

from django.http import HttpRequest
from django.test import TestCase
# from mock import Mock, patch
from censusdata.views import minority_aggregation_as_json, assemble_stats, odds_ratio, get_minority_area_stats
from hmda.views import loan_originations_as_json
from geo.models import Geo
from respondents.models import Institution

params = {'lender': '90000451965', 'metro': '49180'}
request = HttpRequest()
for param in params:
    request.GET[param]=params[param]

class ViewsUtilitiesTests(TestCase):
    fixtures = ['agency.json', 'fake_msa.json', 'api_tracts.json', 'test_counties.json', 'fake_respondents.json']

    def test_minority_aggregation_as_json(self):
        """should return a dict of 5 dicts returning minority values"""
        keys = ['counties', 'msa']
        lender_keys = ['hma_pct', 'lma_pct', 'mma_pct', 'lma', 'mma', 'hma', 'lar_total', 'peer_hma_pct', 'peer_lma_pct', 'peer_mma_pct', 'peer_lma', 'peer_mma', 'peer_hma', 'peer_lar_total', 'odds_lma', 'odds_mma', 'odds_hma']
        result_dict = minority_aggregation_as_json(request)
        self.assertTrue(isinstance(result_dict, dict))
        for key in keys:
            self.assertTrue(key in result_dict.keys())
        for key in lender_keys:
                self.assertTrue(key in result_dict['msa'].keys())
        self.assertTrue(len(result_dict['msa']) > 0)
        self.assertEqual(result_dict['msa']['lar_total'], 0)
        self.assertIsNone(result_dict['msa']['odds_lma'])

    def test_assemble_stats(self):
        """should calculate and return a dict of lender loan totals by minority area"""
        lar_data = loan_originations_as_json(request)
        lender = Institution.objects.get(institution_id=request.GET.get('lender'))
        metro = Geo.objects.get(geo_type=Geo.METRO_TYPE, geoid=request.GET.get('metro'))
        peer_request = HttpRequest()
        peer_request.GET['lender'] = lender.institution_id
        peer_request.GET['metro'] = metro.geoid
        peer_request.GET['peers'] = 'true'
        peer_request.GET['action_taken'] = '1,2,3,4,5'
        peer_lar_data = loan_originations_as_json(peer_request)
        tracts = Geo.objects.filter(geo_type=Geo.TRACT_TYPE, cbsa=metro.cbsa)
        lender_stats = assemble_stats(*get_minority_area_stats(lar_data, peer_lar_data, tracts))
        self.assertEqual(lender_stats['hma_pct'], 0)
        self.assertEqual(lender_stats['lma_pct'], 1)
        self.assertEqual(lender_stats['mma_pct'], 0)
        self.assertEqual(lender_stats['lma'], 3)
        self.assertEqual(lender_stats['mma'], 0)
        self.assertEqual(lender_stats['hma'], 0)
        self.assertEqual(lender_stats['lar_total'], 3)

    def test_odds_ratio(self):
        """
        should return demical representing the odds ratio
        for a lender/MSA pair compared with the lender's peers
        """
        odds1 = odds_ratio(1, 1)
        odds2 = odds_ratio(2, 5)
        odds3 = odds_ratio(0.2, 0.3)
        odds4 = odds_ratio(0.5, 0.5)
        self.assertEqual(odds1, 1.0)
        self.assertEqual(odds2, 0.0)
        self.assertEqual(odds3, 0.583)
        self.assertEqual(odds4, 1.0)
        self.assertIsNone(odds_ratio(1, 0))
        self.assertIsNone(odds_ratio(0, 0))
        self.assertEqual(0, odds_ratio(0, 1))




