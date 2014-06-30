from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import Mock, patch

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


class ViewTest(TestCase):
    fixtures = ['agency']

    @patch('respondants.views.SearchQuerySet')
    def test_search_empty(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        self.client.get(reverse('search'))
        self.assertFalse(SQS.filter.called)

        self.client.get(reverse('search'), {'q': ''})
        self.assertFalse(SQS.filter.called)

        self.client.get(reverse('search'), {'q': '     '})
        self.assertFalse(SQS.filter.called)

    @patch('respondants.views.SearchQuerySet')
    def test_search_name(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result1, result2 = Mock(), Mock()
        SQS.filter.return_value = [result1, result2]
        result1.object = {'name': 'Some Bank'}
        result2.object = {'name': 'Bank & Loan'}
        resp = self.client.get(reverse('search'), {'q': 'Bank'})
        self.assertTrue('Bank' in str(SQS.filter.call_args))
        self.assertTrue('content' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertTrue('Bank &amp; Loan' in resp.content)

    @patch('respondants.views.SearchQuerySet')
    def test_search_id(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.object = Mock()
        result.object.name, result.object.id = 'Some Bank', 1234

        resp = self.client.get(reverse('search'), {'q': '01234567'})
        self.assertTrue('01234567' in str(SQS.filter.call_args))
        self.assertTrue('content' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)

        resp = self.client.get(reverse('search'), {'q': '01234567899'})
        self.assertTrue('01234567899' in str(SQS.filter.call_args))
        self.assertFalse('content' in str(SQS.filter.call_args))
        self.assertTrue('lender_id' in str(SQS.filter.call_args))
        self.assertEqual(resp.status_code, 302)
