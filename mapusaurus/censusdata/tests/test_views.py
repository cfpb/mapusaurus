import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from censusdata.models import Census2010RaceStats
from hmda.models import LendingStats
import api

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
        lendstats = LendingStats(
            geo_id='10000', institution_id="736-4045996",
            lar_median=3, lar_count=4,
            fha_count=2, fha_bucket=2)
        lendstats.save()

    def tearDown(self):
        Census2010RaceStats.objects.all().delete()


    def test_race_summary(self):
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'neLat':'0',
                                    'neLon':'1',
                                    'swLat':'0',
                                    'swLon':'1',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        resp = json.loads(resp.content)
        self.assertEqual(len(resp), 4)
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

