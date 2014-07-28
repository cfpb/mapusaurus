import json

from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from mock import Mock, patch

from respondants import views, zipcode_utils
from respondants.models import Institution, ZipcodeCityState
from respondants.management.commands import load_reporter_panel
from respondants.management.commands import load_transmittal


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


class LoadTransmittalTests(TestCase):
    fixtures = ['agency']

    @patch('__builtin__.open')
    def test_handle(self, mock_open):
        # Only care inside a "with"
        mock_open = mock_open.return_value.__enter__.return_value
        line = "2012\t0000055547\t1\tTAXIDHERE\tFIRST FAKE BK NA\t"
        line += "1122 S 3RD ST\tTERRE HAUTE\tCA\t90210\t"
        line += "FIRST FAKE CORPORATION\tONE ADDR\tTERRE HAUTE\tCA\t90210\t"
        line += "FIRST FAKE BK NA\tTERRE HAUTE\tCA\t121212\t0\t3\t3657\tN"
        mock_open.__iter__.return_value = [line]

        cmd = load_transmittal.Command()
        cmd.handle('somefile.txt')

        query = Institution.objects.all()
        self.assertEqual(query.count(), 1)
        inst = query[0]
        self.assertEqual(inst.name, 'FIRST FAKE BK NA')
        self.assertEqual(inst.ffiec_id, '0000055547')
        self.assertEqual(inst.agency_id, 1)
        self.assertEqual(inst.assets, 121212)


class ViewTest(TestCase):
    fixtures = ['agency']

    @patch('respondants.views.SearchQuerySet')
    def test_search_empty(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        self.client.get(reverse('respondants:search'))
        self.assertFalse(SQS.filter.called)

        self.client.get(reverse('respondants:search'), {'q': ''})
        self.assertFalse(SQS.filter.called)

        self.client.get(reverse('respondants:search'), {'q': '     '})
        self.assertFalse(SQS.filter.called)

    @patch('respondants.views.SearchQuerySet')
    def test_search_name(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result1, result2 = Mock(), Mock()
        SQS.filter.return_value = [result1, result2]
        result1.object.name = 'Some Bank'
        result2.object.name = 'Bank & Loan'
        resp = self.client.get(reverse('respondants:search'), {'q': 'Bank'})
        self.assertTrue('Bank' in str(SQS.filter.call_args))
        self.assertTrue('content' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertTrue('Bank &amp; Loan' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

    @patch('respondants.views.SearchQuerySet')
    def test_search_autocomplete(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.object.name, result.object.id = 'Some Bank', 1234
        self.client.get(reverse('respondants:search'),
                        {'q': 'Bank', 'auto': '1'})
        self.assertTrue('Bank' in str(SQS.filter.call_args))
        self.assertFalse('content' in str(SQS.filter.call_args))
        self.assertTrue('text_auto' in str(SQS.filter.call_args))

    @patch('respondants.views.SearchQuerySet')
    def test_search_id(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.object.name, result.object.id = 'Some Bank', 1234

        resp = self.client.get(reverse('respondants:search'),
                               {'q': '01234567'})
        self.assertTrue('01234567' in str(SQS.filter.call_args))
        self.assertTrue('content' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

        resp = self.client.get(reverse('respondants:search'),
                               {'q': '012345-7899'})
        self.assertTrue('012345-7899' in str(SQS.filter.call_args))
        self.assertFalse('content' in str(SQS.filter.call_args))
        self.assertTrue('lender_id' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

        for q in ['11234567-99', '01-1234567-99', '1234567-99-01',
                  'Some Bank (01-1234567-99)']:
            resp = self.client.get(reverse('respondants:search'), {'q': q})
            self.assertTrue('11234567-99' in str(SQS.filter.call_args))
            self.assertFalse('content' in str(SQS.filter.call_args))
            self.assertTrue('lender_id' in str(SQS.filter.call_args))
            self.assertTrue('Some Bank' in resp.content)
            self.assertRaises(ValueError, json.loads, resp.content)

        resp = self.client.get(reverse('respondants:search'),
                               {'q': 'Some Bank (01-123457-99)'})
        self.assertTrue('01-123457-99' in str(SQS.filter.call_args))
        self.assertTrue('content' in str(SQS.filter.call_args))
        self.assertFalse('lender_id' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

    @patch('respondants.views.SearchQuerySet')
    def test_search_json(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.object = Institution(name='Some Bank')

        resp = self.client.get(reverse('respondants:search'), {'q': 'Bank'},
                               HTTP_ACCEPT='application/json')
        resp = json.loads(resp.content)
        self.assertEqual(1, len(resp['institutions']))
        inst = resp['institutions'][0]
        self.assertEqual('Some Bank', inst['name'])

    @patch('respondants.views.SearchQuerySet')
    def test_search_num_loans(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.num_loans = 45
        result.object = Institution(name='Some Bank')

        request = RequestFactory().get('/', data={'q': 'Bank'})
        results = views.search(request)
        self.assertEqual(len(results.data['institutions']), 1)
        self.assertEqual(45, results.data['institutions'][0].num_loans)

    @patch('respondants.views.SearchQuerySet')
    def test_search_sort(self, SQS):
        load_all = SQS.return_value.models.return_value.load_all.return_value

        request = RequestFactory().get('/', data={'q': 'Bank'})
        views.search(request)
        self.assertFalse(load_all.order_by.called)

        request = RequestFactory().get('/', data={'q': 'Bank',
                                                  'sort': 'another-sort'})
        views.search(request)
        self.assertFalse(load_all.order_by.called)

        for sort in ('assets', '-assets', 'num_loans', '-num_loans'):
            request = RequestFactory().get('/', data={'q': 'Bank',
                                                      'sort': sort})
            views.search(request)
            self.assertTrue(load_all.order_by.called)
