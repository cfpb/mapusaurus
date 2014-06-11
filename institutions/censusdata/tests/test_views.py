import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from censusdata.models import Census2010RaceStats
from censusdata import views


class ViewsTest(TestCase):
    fixtures = ['dummy_tracts']

    def setUp(self):
        stats = Census2010RaceStats(
            total_pop=10, hispanic=1, non_hisp_white_only=2,
            non_hisp_black_only=4, non_hisp_asian_only=5)
        stats.geoid_id = '1122233300'
        stats.save()
        stats = Census2010RaceStats(
            total_pop=20, hispanic=2, non_hisp_white_only=1,
            non_hisp_black_only=5, non_hisp_asian_only=4)
        stats.geoid_id = '1122233400'
        stats.save()
        stats = Census2010RaceStats(
            total_pop=100, hispanic=10, non_hisp_white_only=20,
            non_hisp_black_only=30, non_hisp_asian_only=4)
        stats.geoid_id = '1122333300'
        stats.save()
        stats = Census2010RaceStats(
            total_pop=100, hispanic=0, non_hisp_white_only=0,
            non_hisp_black_only=0, non_hisp_asian_only=7)
        stats.geoid_id = '1222233300'
        stats.save()

    def tearDown(self):
        Census2010RaceStats.objects.all().delete()

    def test_race_summary_400s(self):
        resp = self.client.get(reverse('censusdata:race_summary'))
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'county_fips': '1'})
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'state_fips': '1'})
        self.assertEqual(400, resp.status_code)

    def test_race_summary(self):
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'state_fips': '11', 'county_fips': '222'})
        resp = json.loads(resp.content)
        self.assertEqual(len(resp), 2)
        self.assertTrue('1122233300' in resp)
        self.assertEqual(resp['1122233300']['total_pop'], 10)
        self.assertEqual(resp['1122233300']['hispanic'], 1)
        self.assertEqual(resp['1122233300']['non_hisp_white_only'], 2)
        self.assertEqual(resp['1122233300']['non_hisp_black_only'], 4)
        self.assertEqual(resp['1122233300']['non_hisp_asian_only'], 5)
        self.assertEqual(resp['1122233300']['hispanic_perc'], .1)
        self.assertEqual(resp['1122233300']['non_hisp_white_only_perc'], .2)
        self.assertEqual(resp['1122233300']['non_hisp_black_only_perc'], .4)
        self.assertEqual(resp['1122233300']['non_hisp_asian_only_perc'], .5)
        self.assertTrue('1122233400' in resp)
        self.assertEqual(resp['1122233400']['total_pop'], 20)
        self.assertEqual(resp['1122233400']['hispanic'], 2)
        self.assertEqual(resp['1122233400']['non_hisp_white_only'], 1)
        self.assertEqual(resp['1122233400']['non_hisp_black_only'], 5)
        self.assertEqual(resp['1122233400']['non_hisp_asian_only'], 4)
        self.assertEqual(resp['1122233400']['hispanic_perc'], .1)
        self.assertEqual(resp['1122233400']['non_hisp_white_only_perc'], .05)
        self.assertEqual(resp['1122233400']['non_hisp_black_only_perc'], .25)
        self.assertEqual(resp['1122233400']['non_hisp_asian_only_perc'], .2)

    def test_split_binned_and_raw_fields(self):

        requested_fields = [
            {
                'name': 'non_hisp_asian_only_perc',
                'type': 'binned',
                'bins': [0, 0.5, 0.8, 1.01]},
            {
                'name': 'total_pop',
                'type': 'raw'}]

        bins, raw_fields = views.split_binned_and_raw_fields(requested_fields)
        self.assertEqual(['total_pop'], raw_fields)

        bins_result = {
            'non_hisp_asian_only_perc': {
                'values': [], 'bins': [0, 0.5, 0.8, 1.01]}}

        self.assertEqual(bins_result, bins)

    def test_collect_field_values(self):
        bins = {
            'non_hisp_asian_only_perc': {
                'values': [], 'bins': [0, 0.5, 0.8, 1.01]}}

        tract_data = Census2010RaceStats.objects.all()
        bins, statsids = views.collect_field_values(tract_data, bins)

        self.assertEqual(
            ['1122233300', '1122233400', '1122333300', '1222233300'],
            statsids)

        self.assertEqual(
            [0.5, 0.2, 0.04, 0.07],
            bins['non_hisp_asian_only_perc']['values'])

    def test_find_bin_indices(self):
        field = {
            'bins': [0.5, 0.75, 1.0],
            'values': [0.5, 0.6, 0.8, 0.95]
        }

        indices = views.find_bin_indices(field)
        self.assertEqual([1, 1, 2, 2], list(indices))

    def test_find_all_bin_indices(self):
        bins = {
            'non_hisp_asian_only_perc': {
                'values': [0.5, 0.6, 0.8, 0.95], 'bins': [0.5, 0.75, 1.0]}}

        statsids = [4, 2, 3, 1]

        bins_results = views.find_all_bin_indices(bins, statsids)
        self.assertEqual(
            {1: 2, 2: 1, 3: 2, 4: 1},
            bins_results['non_hisp_asian_only_perc']['bin_indices'])
