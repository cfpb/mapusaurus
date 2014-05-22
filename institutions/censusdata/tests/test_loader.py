import os
import shutil
import tempfile

from django.test import TestCase
from mock import patch

from censusdata import models
from censusdata.management.commands.load_summary_one import Command


class LoadSummaryDataTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @patch.object(Command, 'handle_filefour')
    @patch.object(Command, 'handle_filethree')
    def test_handle(self, hft, hff):
        # Create Mock GEO file
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_geo.txt"),
                        os.path.join(self.tempdir, "ZZgeo2010.sf1"))

        command = Command()
        command.handle(os.path.join(self.tempdir, 'ZZgeo2010.sf1'))
        positional_args = hft.call_args[0]
        self.assertEqual(positional_args[0],
                         os.path.join(self.tempdir, "ZZgeo2010.sf1"))
        self.assertEqual(len(positional_args[1]), 2)
        self.assertEqual(positional_args[1]['0007159'], '11001000100')
        self.assertEqual(positional_args[1]['0007211'], '11001000902')

    def test_handle_filethree(self):
        shutil.copyfile(os.path.join("censusdata", "tests", "mock_file3.txt"),
                        os.path.join(self.tempdir, "ZZ000032010.sf1"))
        command = Command()
        command.handle_filethree(os.path.join(self.tempdir, "ZZgeo2010.sf1"),
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
