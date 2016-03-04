import json

from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from mock import Mock, patch

from geo.models import Geo
from hmda.models import HMDARecord
from respondents import views, zipcode_utils
from respondents.models import Agency, Institution, ZipcodeCityStateYear
from respondents.management.commands import load_reporter_panel
from respondents.management.commands import load_transmittal
from respondents.search_indexes import InstitutionIndex

class ZipcodeUtilsTests(TestCase):
    def test_createzipcode(self):
        ZipcodeCityStateYear.objects.all().delete()
        zipcode_utils.create_zipcode('20852', 'Rockville', 'MD', '2013')

        results = ZipcodeCityStateYear.objects.filter(state='MD')
        self.assertEqual(1, len(results))

        self.assertEqual(results[0].zip_code, 20852)
        self.assertEqual(results[0].city, 'Rockville')
        self.assertEqual(results[0].state, 'MD')
        self.assertEqual(results[0].year, 2013)


    def test_duplicate_entries(self):
        """ We insert a duplicate entry, and check that it wasn't in fact
        duplicated. """
        zipcode_utils.create_zipcode('20852', 'Rockville', 'MD','2013')
        results = ZipcodeCityStateYear.objects.filter(state='MD')
        self.assertEqual(1, len(results))


class ReporterPanelLoadingTests(TestCase):
    def test_parseline(self):
        reporter_line = "201400000555471                                                                   0312328543920FIRST FAKE BK NA                                                      TERRE HAUTE              CA                    0001208595FIRST FC                      TERRE HAUTE              CAUNITED STATES                           0000693345001234000018"
        reporter_row = load_reporter_panel.parse_line(reporter_line)
        self.assertEqual('2014', reporter_row.year)
        self.assertEqual('0000055547', reporter_row.respondent_id)
        self.assertEqual(1, reporter_row.agency_code)
        self.assertEqual('', reporter_row.parent_id)


class LoadTransmittalTests(TestCase):
    fixtures = ['agency']

    @patch('__builtin__.open')
    def test_handle(self, mock_open):
        # Only care inside a "with"
        mock_open = mock_open.return_value.__enter__.return_value
        line = "2013\t0000055547\t1\tTAXIDHERE\tFIRST FAKE BK NA\t"
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
        self.assertEqual(inst.respondent_id, '0000055547')
        self.assertEqual(inst.agency_id, 1)
        self.assertEqual(inst.assets, 121212)

class LenderHierarchyTest(TestCase):
    fixtures = ['agency', 'fake_respondents', 'fake_hierarchy']

    def test_get_lender_hierarchy(self):
        """Case: Institution has no hierarchy"""
        institution = Institution.objects.filter(institution_id="11000000002").first()
        hierarchy_list = institution.get_lender_hierarchy(False, False, 2013)
        self.assertEqual(len(hierarchy_list), 0) 
        
        """Case: Institution has no hierarchy but itself. 
           Returns itself when exclude=False; Returns empy list when exclude=True
        """
        institution = Institution.objects.filter(institution_id="91000000003").first()
        hierarchy_list = institution.get_lender_hierarchy(False, False, 2013)
        self.assertEqual(len(hierarchy_list), 1)
        self.assertEqual(hierarchy_list[0].institution_id, "91000000003")
        hierarchy_list_exclude = institution.get_lender_hierarchy(True, False, 2013)
        self.assertEqual(len(hierarchy_list_exclude), 0)

        """Case: Institution has valid hierarchy and returns it""" 
        institution = Institution.objects.filter(institution_id="91000000001").first()
        hierarchy_list = institution.get_lender_hierarchy(False, False,2013)
        self.assertEqual(len(hierarchy_list), 3)
        hierarchy_list_exclude = institution.get_lender_hierarchy(True, False, 2013)
        self.assertEqual(len(hierarchy_list_exclude), 2)
        hierarchy_list_order = institution.get_lender_hierarchy(False, True, 2013)
        self.assertEqual(hierarchy_list_order[0].institution_id, "91000000001")
        hierarchy_list_exclude_order = institution.get_lender_hierarchy(True, True, 2013)
        self.assertEqual(hierarchy_list_exclude_order[0].institution_id, "91000000002")        
        self.assertEqual(len(hierarchy_list_exclude_order), 2)

class ViewTest(TestCase):
    fixtures = ['agency', 'fake_respondents', 'fake_hierarchy', 'fake_branches', 'fake_year']
 
    def test_branch_locations(self):
        resp = self.client.get(reverse('branchLocations'), 
            {'lender':'91000000001',
            'neLat':'1',
            'neLon':'1',
            'swLat':'0',
            'swLon':'0'})
        resp = json.loads(resp.content)
        self.assertEquals('91000000001', resp['features'][0]['properties']['institution_id'])
        self.assertEquals('Dev Test Branch 2', resp['features'][0]['properties']['name'])
        self.assertEquals('91000000001', resp['features'][1]['properties']['institution_id'])
        self.assertEquals('Dev Test Branch 1', resp['features'][1]['properties']['name'])

    def test_select_metro(self):
        results = self.client.get(
            reverse('respondents:select_metro',
                    kwargs={'agency_id': '0', 'respondent': '0987654321', 'year': 2013}))
        self.assertEqual(404, results.status_code)

        zipcode = ZipcodeCityStateYear.objects.create(
            zip_code=12345, city='City', state='IL', year=1234)
        inst = Institution.objects.create(
            year=1234, respondent_id='9879879870', agency=Agency.objects.get(pk=9),
            tax_id='1111111111', name='Institution', mailing_address='mail',
            zip_code=zipcode)

        results = self.client.get(
            reverse('respondents:select_metro',
                    kwargs={'agency_id': '9', 'respondent': '9879879870', 'year': 1234}))
        self.assertEqual(200, results.status_code)

        inst.delete()
        zipcode.delete()

    @patch('respondents.views.SearchQuerySet')
    def test_search_empty(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        self.client.get(reverse('respondents:search_results'))
        self.assertFalse(SQS.filter.called)

        self.client.get(reverse('respondents:search_results'), {'q': '', 'year': '2013'})
        self.assertFalse(SQS.filter.called)

        self.client.get(reverse('respondents:search_results'), {'q': '     ', 'year': ''})
        self.assertFalse(SQS.filter.called)

    @patch('respondents.views.SearchQuerySet')
    def test_search_name(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value.order_by.return_value

        result1, result2 = Mock(), Mock()
        SQS.filter.return_value = [result1, result2]

        result1.object.name = 'Some Bank'
        result1.object.assets = 201
        result1.object.agency_id = 1
        result1.object.respondent_id = '0123456789'
        result1.object.year = '2013'
        result2.object.name = 'Bank & Loan'
        result1.object.assets = 202
        result2.object.agency_id = 2
        result2.object.respondent_id = '1122334455'
        result2.object.year = '2013'
        resp = self.client.get(reverse('respondents:search_results'),
                               {'q': 'Bank', 'year': '2013'})


        self.assertTrue('Bank' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertTrue('Bank &amp; Loan' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)


    @patch('respondents.views.SearchQuerySet')
    def test_search_autocomplete(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value.order_by.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.object.name, result.object.id = 'Some Bank', 1234
        result.object.year, result.object.agency_id, result.object.respondent_id = 2013, 3, '3232434354'
        self.client.get(reverse('respondents:search_results'),
                        {'q': 'Bank', 'auto': '1', 'year': '2013'})
        self.assertTrue('Bank' in str(SQS.filter.call_args))
        self.assertTrue('text_auto' in str(SQS.filter.call_args))

    @patch('respondents.views.SearchQuerySet')
    def test_search_id(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value.order_by.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.object.name, result.object.id = 'Some Bank', 1234
        result.object.year, result.object.agency_id, result.object.respondent_id = 2013, 3, '1234543210'

        resp = self.client.get(reverse('respondents:search_results'),
                               {'q': '01234567', 'year': '2013'})

        self.assertTrue('01234567' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

        resp = self.client.get(reverse('respondents:search_results'),
                               {'q': '012345-7899', 'year': '2013'})
        self.assertTrue('012345-7899' in str(SQS.filter.call_args))
        self.assertTrue('lender_id' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

        for q in ['01123456799',
                  'Some Bank (01123456799)']:
            resp = self.client.get(reverse('respondents:search_results'),
                                   {'q': q, 'year': '2013'})
            self.assertTrue('01123456799' in str(SQS.filter.call_args))
            self.assertTrue('lender_id' in str(SQS.filter.call_args))
            self.assertTrue('Some Bank' in resp.content)
            self.assertRaises(ValueError, json.loads, resp.content)

        resp = self.client.get(reverse('respondents:search_results'),
                               {'q': 'Some Bank (0112345799)', 'year': '2013'})
        self.assertTrue('0112345799' in str(SQS.filter.call_args))
        self.assertFalse('lender_id' in str(SQS.filter.call_args))
        self.assertTrue('Some Bank' in resp.content)
        self.assertRaises(ValueError, json.loads, resp.content)

    @patch('respondents.views.SearchQuerySet')
    def test_search_json(self, SQS):
        #SQS = SQS.return_value.models.return_value.load_all.return_value.order_by_
        SQS = SQS.return_value.models.return_value.load_all.return_value.order_by.return_value
        result = Mock()
        SQS.filter.return_value = [result]

        result.object = Institution(name='Some Bank')

        resp = self.client.get(reverse('respondents:search_results'),
                               {'q': 'Bank', 'year': '2013'},
                               HTTP_ACCEPT='application/json')

        resp = json.loads(resp.content)
        self.assertEqual(1, len(resp['institutions']))
        inst = resp['institutions'][0]
        self.assertEqual('Some Bank', inst['name'])

    @patch('respondents.views.SearchQuerySet')
    def test_search_num_loans(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value.order_by.return_value
        result = Mock()
        SQS.filter.return_value = [result]
        result.num_loans = 45
        result.object = Institution(name='Some Bank')

        request = RequestFactory().get('/', data={'q': 'Bank', 'year': '2013'})
        results = views.search_results(request)
        self.assertEqual(len(results.data['institutions']), 1)
        self.assertEqual(45, results.data['institutions'][0].num_loans)

    @patch('respondents.views.SearchQuerySet')
    def test_search_sort(self, SQS):

        load_all = SQS.return_value.models.return_value.load_all.return_value

        request = RequestFactory().get('/', data={'q': 'Bank'})
        views.search_results(request)
        self.assertTrue(load_all.order_by.called)

        request = RequestFactory().get('/', data={'q': 'Bank',
                                                  'sort': 'another-sort', 'year': '2013'})
        views.search_results(request)
        self.assertTrue(load_all.order_by.called)

        for sort in ('assets', '-assets', 'num_loans', '-num_loans'):
            request = RequestFactory().get('/', data={'q': 'Bank',
                                                      'sort': sort, 'year': '2013'})
            views.search_results(request)
            self.assertTrue(load_all.order_by.called)

    @patch('respondents.views.SearchQuerySet')
    def test_search_pagination(self, SQS):
        request = RequestFactory().get('/', data={'q': 'Bank', 'year': '2013'})
        results = views.search_results(request)
        # page number should default to 1
        self.assertEqual(results.data['page_num'], 1)

        request = RequestFactory().get('/', data={'q': 'Bank',
                                                  'page': 3, 'year': '2013'})
        results = views.search_results(request)
        self.assertEqual(results.data['page_num'], 3)
        self.assertEqual(results.data['next_page'], 0)
        self.assertEqual(results.data['prev_page'], 2)

        request = RequestFactory().get('/', data={'q': 'Bank',
                                                  'page': 'str', 'year': '2013'})
        results = views.search_results(request)
        self.assertEqual(results.data['page_num'], 1)

    @patch('respondents.views.SearchQuerySet')
    def test_search_num_results(self, SQS):
        request = RequestFactory().get('/', data={'q': 'Bank', 'year': '2013'})
        results = views.search_results(request)
        # number of results should default to 25
        self.assertEqual(results.data['num_results'], 25)

        request = RequestFactory().get('/', data={'q': 'Bank',
                                                  'num_results': 10, 'year': '2013'})
        results = views.search_results(request)
        self.assertEqual(results.data['num_results'], 10)

        request = RequestFactory().get('/', data={'q': 'Bank',
                                                  'num_results': 'str', 'year': '2013'})
        results = views.search_results(request)
        self.assertEqual(results.data['num_results'], 25)

class InstitutionIndexTests(TestCase):
    fixtures = ['agency', 'many_tracts']

    def setUp(self):
        self.zipcode = ZipcodeCityStateYear.objects.create(
            zip_code=12345, city='City', state='IL', year='2013')
        self.inst1 = Institution.objects.create(
            year=1234, respondent_id='9876543210', agency=Agency.objects.get(pk=9),
            institution_id='99876543210', tax_id='1111111111', name='Institution', mailing_address='mail',
            zip_code=self.zipcode)
        self.inst2 = Institution.objects.create(
            year=1234, respondent_id='0123456789', agency=Agency.objects.get(pk=9),
            institution_id='90123456789', tax_id='2222222222', name='Institution', mailing_address='mail',
            zip_code=self.zipcode)
        self.hmda = HMDARecord.objects.create(
            as_of_year=2005, respondent_id='9876543210', agency_code='9',
            loan_type=1, property_type=1, loan_purpose=1, owner_occupancy=1,
            loan_amount_000s=100, preapproval='1', action_taken=4,
            msamd='01234', statefp='00', countyfp='000',
            census_tract_number ='01234', applicant_ethnicity='1',
            co_applicant_ethnicity='1', applicant_race_1='1', co_applicant_race_1='1',
            applicant_sex='1', co_applicant_sex='1', applicant_income_000s='1000',
            purchaser_type='1', rate_spread='0123', hoepa_status='1', lien_status='1',
            sequence_number='1', population='1', minority_population='1',
            ffieic_median_family_income='1000', tract_to_msamd_income='1000',
            number_of_owner_occupied_units='1', number_of_1_to_4_family_units='1',
            application_date_indicator=1, institution=self.inst1, geo=Geo.objects.all()[0])
    def tearDown(self):
        self.hmda.delete()
        self.inst2.delete()
        self.inst1.delete()
        self.zipcode.delete()

    def test_queryset_num_loans(self):
        found1, found2 = False, False
        index = InstitutionIndex()
        for obj in index.index_queryset():
            if obj.respondent_id == '9876543210':
                found1 = True
                self.assertEqual(obj.num_loans, 1)
            elif obj.respondent_id == '0123456789':
                found2 = True
        self.assertTrue(found1)
        self.assertFalse(found2)

    def test_queryset_read(self):
        found = False
        index = InstitutionIndex()
        for obj in index.read_queryset():
            found = True
            self.assertFalse(hasattr(obj, 'num_loans'))
        self.assertTrue(found)
