import os
import shutil
import tempfile

from django.test import TestCase
from mock import patch

from censusdata import models
from censusdata.management.commands.load_summary_one import Command

import geo.errors

class LoadSummaryDataTest(TestCase):
    fixtures = ['mock_geo']

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @patch.object(Command, 'handle_filefive')
    @patch.object(Command, 'handle_filefour')
    @patch.object(Command, 'handle_filethree')
    def test_handle(self, hf3, hf4, hf5):
        # Create Mock GEO file
        year = '2013'
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_geo.txt"),
                        os.path.join(self.tempdir, "ZZgeo2010.sf1"))

        command = Command()
        command.handle(os.path.join(self.tempdir, 'ZZgeo2010.sf1'), year)
        positional_args = hf4.call_args[0]
        self.assertEqual(positional_args[0],
                         os.path.join(self.tempdir, "ZZgeo2010.sf1"))
        self.assertEqual(positional_args[1], year)
        self.assertEqual(positional_args[2], '11')  # State
        self.assertEqual(len(positional_args[3]), 2)
        self.assertEqual(positional_args[3]['0007159'], year+'11001000100')
        self.assertEqual(positional_args[3]['0007211'], year+'11001000902')

    @patch.object(Command, 'handle_filefive')
    @patch.object(Command, 'handle_filefour')
    @patch.object(Command, 'handle_filethree')
    def test_handle_errors_dict(self, hf3, hf4, hf5):
        year = '2001'
        old_geo_errors = geo.errors.in_2010
        geo.errors.in_2010 = {'11001000100': '22002000200', '11001000902': None}

        # Create Mock GEO file
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_geo.txt"),
                        os.path.join(self.tempdir, "ZZgeo2010.sf1"))

        command = Command()
        command.handle(os.path.join(self.tempdir, 'ZZgeo2010.sf1'), year)
        positional_args = hf4.call_args[0]
        # The None causes us to skip 11001000902
        self.assertEqual(len(positional_args[2]), 2)
        # This entry was converted
        self.assertEqual(positional_args[3]['0007159'], year+'22002000200')

        geo.errors.in_2010 = old_geo_errors

    def test_handle_filethree(self):
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_file3.txt"),
                        os.path.join(self.tempdir, "ZZ000032010.sf1"))
        command = Command()
        command.handle_filethree(os.path.join(self.tempdir, "ZZgeo2010.sf1"),
                                 '2013', '11',  # State
                                 {'0007159': '11001000100',
                                  '0007211': '11001000902'})
        model = models.Census2010RaceStats.objects.get(pk='11001000100')
        self.assertEqual(model.total_pop, 4890)
        self.assertEqual(model.hispanic, 296)
        self.assertEqual(model.non_hisp_white_only, 4202)
        self.assertEqual(model.non_hisp_black_only, 101)
        self.assertEqual(model.non_hisp_asian_only, 198)
        model.delete()

        model = models.Census2010RaceStats.objects.get(pk='11001000902')
        self.assertEqual(model.total_pop, 2092)
        self.assertEqual(model.hispanic, 107)
        self.assertEqual(model.non_hisp_white_only, 1776)
        self.assertEqual(model.non_hisp_black_only, 63)
        self.assertEqual(model.non_hisp_asian_only, 77)
        model.delete()

        self.assertEqual(len(models.Census2010RaceStats.objects.all()), 0)

    def test_handle_filethree_no_delete(self):
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_file3.txt"),
                        os.path.join(self.tempdir, "ZZ000032010.sf1"))
        command = Command()
        command.handle_filethree(os.path.join(self.tempdir, "ZZgeo2010.sf1"),
                                 '2013', '11',  # State
                                 {'0007159': '11001000100',
                                  '0007211': '11001000902'})
        self.assertEqual(len(models.Census2010RaceStats.objects.all()), 2)
        models.Census2010RaceStats.objects.all()[0].delete()
        self.assertEqual(len(models.Census2010RaceStats.objects.all()), 1)

        # Importing again should do nothing
        command.handle_filethree(os.path.join(self.tempdir, "ZZgeo2010.sf1"),
                                 '2013', '11',  # State
                                 {'0007159': '11001000100',
                                  '0007211': '11001000902'})
        self.assertEqual(len(models.Census2010RaceStats.objects.all()), 1)
        models.Census2010RaceStats.objects.all().delete()

    def test_handle_filefive(self):
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_file5.txt"),
                        os.path.join(self.tempdir, "ZZ000052010.sf1"))
        command = Command()
        command.handle_filefive(os.path.join(self.tempdir, "ZZgeo2010.sf1"),
                                '2013', '11',  # State
                                {'0007159': '11001000100',
                                 '0007211': '11001000902'})
        model = models.Census2010Households.objects.get(pk='11001000100')
        self.assertEqual(model.total, 1853624)
        self.assertEqual(model.total_family, 1067203)
        self.assertEqual(model.total_nonfamily, 786421)
        model.delete()

        model = models.Census2010Households.objects.get(pk='11001000902')
        self.assertEqual(model.total, 2738936)
        self.assertEqual(model.total_family, 1951351)
        self.assertEqual(model.total_nonfamily, 787585)
        model.delete()

        self.assertEqual(len(models.Census2010Households.objects.all()), 0)
