from django.test import TestCase

from censusdata.models import Census2010RaceStats
from geo.models import Geo


class Census2010RaceStatsTest(TestCase):
    fixtures = ['dummy_tracts']

    def test_auto_populated(self):
        tract = Geo.objects.get(pk='1122233300')
        stats = Census2010RaceStats(
            geoid=tract, total_pop=20, hispanic=1, non_hisp_white_only=2,
            non_hisp_black_only=4, non_hisp_asian_only=5)
        stats.save()
        self.assertEqual(stats.hispanic_perc, 1.0/20)
        self.assertEqual(stats.non_hisp_white_only_perc, 2.0/20)
        self.assertEqual(stats.non_hisp_black_only_perc, 4.0/20)
        self.assertEqual(stats.non_hisp_asian_only_perc, 5.0/20)
        stats.delete()

        stats = Census2010RaceStats(
            geoid=tract, total_pop=20, hispanic=1, non_hisp_white_only=2,
            non_hisp_black_only=4, non_hisp_asian_only=5)
        stats.auto_fields()
        self.assertEqual(stats.hispanic_perc, 1.0/20)
        self.assertEqual(stats.non_hisp_white_only_perc, 2.0/20)
        self.assertEqual(stats.non_hisp_black_only_perc, 4.0/20)
        self.assertEqual(stats.non_hisp_asian_only_perc, 5.0/20)

        stats = Census2010RaceStats(
            geoid=tract, total_pop=0, hispanic=0, non_hisp_white_only=0,
            non_hisp_black_only=0, non_hisp_asian_only=0)
        stats.auto_fields()
        self.assertEqual(stats.hispanic_perc, 1.0)
        self.assertEqual(stats.non_hisp_white_only_perc, 1.0)
        self.assertEqual(stats.non_hisp_black_only_perc, 1.0)
        self.assertEqual(stats.non_hisp_asian_only_perc, 1.0)
