import os

from django.test import TestCase

from hmda.management.commands.load_hmda import Command
from hmda.models import HMDARecord


class LoadHmdaTest(TestCase):
    fixtures = ['dummy_tracts']

    def test_handle(self):
        command = Command()
        command.handle(os.path.join("hmda", "tests", "mock_2014.csv"))

        # The mock data file contains 10 records, 8 for known states
        self.assertEqual(8, HMDARecord.objects.count())
        lenders = set(r.lender for r in HMDARecord.objects.all())
        self.assertEqual(3, len(lenders))
        self.assertTrue(('5' + '0000000319') in lenders)
        self.assertTrue(('5' + '0000000435') in lenders)
        self.assertTrue(('3' + '0000001281') in lenders)

        HMDARecord.objects.all().delete()
