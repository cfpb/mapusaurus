import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from censusdata.models import Census2010RaceStats


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
            total_pop=1, hispanic=10, non_hisp_white_only=20,
            non_hisp_black_only=30, non_hisp_asian_only=40)
        stats.geoid_id = '1122333300'
        stats.save()
        stats = Census2010RaceStats(
            total_pop=100, hispanic=0, non_hisp_white_only=0,
            non_hisp_black_only=0, non_hisp_asian_only=7)
        stats.geoid_id = '1222233300'
        stats.save()

    def tearDown(self):
        Census2010RaceStats.objects.all().delete()

    def test_race_summary_404s(self):
        resp = self.client.get(reverse('censusdata:race_summary'))
        self.assertEqual(404, resp.status_code)
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'county_fips': '1'})
        self.assertEqual(404, resp.status_code)
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'state_fips': '1'})
        self.assertEqual(404, resp.status_code)

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
