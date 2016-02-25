import os

from django.test import TestCase
from mock import Mock, patch

from hmda.management.commands.load_hmda import Command
from hmda.models import HMDARecord
 

class LoadHmdaTest(TestCase):
    fixtures = ['dummy_tracts']

    def test_handle(self):
        command = Command()
        command.stdout = Mock()
        command.handle(os.path.join("hmda", "tests", "mock_2013.csv"),2013)

        # The mock data file contains 10 records, 8 for known states
        self.assertEqual(8, HMDARecord.objects.count())
        lenders = set(r.institution_id for r in HMDARecord.objects.all())
        geos = set(r.geo_id for r in HMDARecord.objects.all())
        self.assertEqual(3, len(lenders))
        self.assertTrue(('2013'+'5' + '0000000319') in lenders)
        self.assertTrue(('2013'+'5' + '0000000435') in lenders)
        self.assertTrue(('2013'+'3' + '0000001281') in lenders)
        self.assertEqual(4, len(geos))
        self.assertTrue('20131122233300' in geos)
        self.assertTrue('20131122233400' in geos)
        self.assertTrue('20131122333300' in geos)
        self.assertTrue('20131222233300' in geos)

        HMDARecord.objects.all().delete()

    @patch('hmda.management.commands.load_hmda.errors')
    def test_handle_errors_dict(self, errors):
        errors.in_2010 = {'1122233300': '9988877766'}
        command = Command()
        command.stdout = Mock()
        command.handle(os.path.join("hmda", "tests", "mock_2013.csv"), '2013')

        geos = set(r.geo_id for r in HMDARecord.objects.all())
        self.assertEqual(4, len(geos))
        # 1122233300 got replaced
        self.assertTrue('20139988877766' in geos)
        self.assertFalse('20131122233300' in geos)

        HMDARecord.objects.all().delete()

    def test_multi_files(self):

        command = Command()
        command.stdout = Mock()

        main_csv_directory = os.path.abspath( os.path.join("hmda", "tests") )

        main_csv_directory = main_csv_directory + "/"

        command.handle(main_csv_directory, '2013', "delete_file:false", "filterhmda")
        lenders = set(r.institution_id for r in HMDARecord.objects.all())
        geos = set(r.geo_id for r in HMDARecord.objects.all())

        self.assertEqual(3, len(lenders))
        self.assertTrue(('2013'+'5' + '0000000319') in lenders)
        self.assertTrue(('2013'+'5' + '0000000435') in lenders)
        self.assertTrue(('2013'+'3' + '0000001281') in lenders)
        self.assertEqual(4, len(geos))
        self.assertTrue('20131122233300' in geos)
        self.assertTrue('20131122233400' in geos)
        self.assertTrue('20131122333300' in geos)
        self.assertTrue('20131222233300' in geos)

        HMDARecord.objects.all().delete()
