from django.test import TestCase
from respondants import zipcode_utils
from respondants.models import ZipcodeCityState
from respondants.management.commands import load_reporter_panel


class ZipcodeUtilsTests(TestCase):
    def test_createzipcode(self):
        ZipcodeCityState.objects.all().delete()
        zipcode_utils.create_zipcode('20852', 'Rockville', 'MD')

        results = ZipcodeCityState.objects.filter(state='MD')
        self.assertEqual(1, len(results))

        self.assertEqual(results[0].zip_code, 20852)
        self.assertEqual(results[0].city, 'Rockville')
        self.assertEqual(results[0].state, 'MD')

    def test_duplicate_entries(self):
        """ We insert a duplicate entry, and check that it wasn't in fact
        duplicated. """
        zipcode_utils.create_zipcode('20852', 'Rockville', 'MD')
        results = ZipcodeCityState.objects.filter(state='MD')
        self.assertEqual(1, len(results))


class ReporterPanelLoadingTests(TestCase):
    def test_parseline(self):
        reporter_line = "201400000555471                                                                   0312328543920FIRST FAKE BK NA                                                      TERRE HAUTE              CA                    0001208595FIRST FC                      TERRE HAUTE              CAUNITED STATES                           0000693345001234000018"
        reporter_row = load_reporter_panel.parse_line(reporter_line)
        self.assertEqual('2014', reporter_row.year)
        self.assertEqual('0000055547', reporter_row.respondant_id)
        self.assertEqual(1, reporter_row.agency_code)
        self.assertEqual('', reporter_row.parent_id)
