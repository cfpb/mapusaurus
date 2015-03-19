"""
tests of the helper functions for assembling tables for map page
"""

from django.http import HttpRequest
from django.test import TestCase
# from mock import Mock, patch
from censusdata.views import minority_aggregation_as_json, assemble_stats, odds_ratio
from hmda.views import loan_originations_as_json
from geo.models import Geo

params = {'lender': '90000451965', 'metro': '49180'}
request = HttpRequest()
for param in params:
    request.GET[param]=params[param]

class ViewsUtilitiesTests(TestCase):
    fixtures = ['agency.json', 'fake_msa.json', 'api_tracts.json', 'test_counties.json', 'fake_respondents.json']

    def test_minority_aggregation_as_json(self):
        """should return a dict of 5 dicts returning minority values"""
        keys = ['target_lender', 'peers', 'odds_msa', 'counties', 'county_odds']
        lender_keys = ['hma_pct', 'lma_pct', 'mma_pct', 'lma', 'mma', 'hma', 'lar_total']
        result_dict = minority_aggregation_as_json(request)
        self.assertTrue(isinstance(result_dict, dict))
        for key in keys:
            self.assertTrue(key in result_dict.keys())
        for key in lender_keys:
                self.assertTrue(key in result_dict['target_lender'].keys())
        self.assertTrue(len(result_dict['counties']) > 0)
        self.assertEqual(result_dict['target_lender']['lar_total'], 7)
        self.assertEqual(result_dict['peers']['lar_total'], 0.0)
        self.assertEqual(result_dict['odds_msa']['odds_msa_lma'], 0.0)
        self.assertEqual(result_dict['counties']['11222']['lma'], 7)
        self.assertEqual(result_dict['counties']['11222']['lar_total'], 7)

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

    def test_odds_ratio(self):
        """
        should return demical representing the odds ratio
        for a lender/MSA pair compared with the lender's peers
        """
        odds1 = odds_ratio(1, 1)# should bail on division by zero and return None
        odds2 = odds_ratio(2, 5)
        odds3 = odds_ratio(0.2, 0.3)
        odds4 = odds_ratio(0.5, 0.5)
        self.assertEqual(odds1, 0.0)
        self.assertEqual(odds2, 0.0)
        self.assertEqual(odds3, 0.583)
        self.assertEqual(odds4, 1.0)




