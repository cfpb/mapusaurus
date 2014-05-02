from django.test import TestCase
from respondants import zipcode_utils
from respondants.models import ZipcodeCityState

# Create your tests here.
class ZipcodeUtilsTests(TestCase):
    def test_createzipcode(self):
        zipcode = zipcode_utils.create_zipcode('20852', 'Rockville', 'MD')
        self.assertEqual(zipcode.pk, 1)

        results = ZipcodeCityState.objects.filter(state='MD')
        self.assertEqual(1, len(results))

        self.assertEqual(results[0].zip_code, 20852)
        self.assertEqual(results[0].city, 'Rockville')
        self.assertEqual(results[0].state, 'MD')


    def test_duplicate_entries(self):
        """ We insert a duplicate entry, and check that it wasn't in fact 
        duplicated. """
        zipcode = zipcode_utils.create_zipcode('20852', 'Rockville', 'MD')
        results = ZipcodeCityState.objects.filter(state='MD')
        self.assertEqual(1, len(results))
