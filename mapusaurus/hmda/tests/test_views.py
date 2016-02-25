import json

from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase
from censusdata.models import Census2010Households
from hmda.models import HMDARecord, LendingStats
from respondents.models import Institution
from geo.models import Geo

class ViewsTest(TestCase):
    fixtures = ['agency', 'fake_respondents', 'dummy_tracts', 'fake_msa']

    def setUp(self):
        stats = Census2010Households(
            None, 100, 80, 50, 30, 20, 10, 20, 15, 5)
        stats.geoid_id = '1122233300'
        stats.save()
        stats = Census2010Households(
            None, 1000, 800, 500, 300, 200, 100, 200, 150, 50)
        stats.geoid_id = '1122233400'
        stats.save()
        stats = Census2010Households(
            None, 200, 160, 100, 60, 40, 20, 40, 30, 10)
        stats.geoid_id = '1222233300'
        stats.save()
   
        def mkrecord(institution_id, action_taken, countyfp, geoid):
            respondent = Institution.objects.get(institution_id=institution_id)
            geo = Geo.objects.get(geoid=geoid)
            record = HMDARecord(
                as_of_year=2014, respondent_id=respondent.respondent_id, agency_code=respondent.agency_id,
                loan_type=1, property_type=1, loan_purpose=1, owner_occupancy=1,
                loan_amount_000s=222, preapproval='1', action_taken=action_taken,
                msamd='01234', statefp='11', countyfp=countyfp,
                census_tract_number ='01234', applicant_ethnicity='1',
                co_applicant_ethnicity='1', applicant_race_1='1', co_applicant_race_1='1',
                applicant_sex='1', co_applicant_sex='1', applicant_income_000s='1000',
                purchaser_type='1', rate_spread='0123', hoepa_status='1', lien_status='1',
                sequence_number='1', population='1', minority_population='1',
                ffieic_median_family_income='1000', tract_to_msamd_income='1000',
                number_of_owner_occupied_units='1', number_of_1_to_4_family_units='1',
                application_date_indicator=1)
            record.geo = geo
            record.institution = respondent
            record.save()

        #institution #1 records, total = 6; selected institution
        mkrecord("91000000001", 1, '222', '1122233300')
        mkrecord("91000000001", 1, '222', '1122233300')
        mkrecord("91000000001", 1, '222', '1122233400')
        mkrecord("91000000001", 1, '222', '1122233300')
        mkrecord("91000000001", 1, '222', '1122233300')
        mkrecord("91000000001", 1, '223', '1122333300')

        #institution #2 records, total = 4; >.5 and <2.0; peer
        mkrecord("91000000002", 1, '222', '1122233300')
        mkrecord("91000000002", 1, '222', '1122233300')
        mkrecord("91000000002", 1, '222', '1122233400')
        mkrecord("91000000002", 1, '222', '1122233300')
        
        #institution #3 records, total =2; <.5; not peer
        mkrecord("91000000003", 1, '222', '1122233300')
        mkrecord("91000000003", 1, '223', '1122333300')

        #institution #4 records, total = 13; >2.0; not peer
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '222', '1122233400')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '223', '1122333300')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '222', '1122233400')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '222', '1122233300')
        mkrecord("11000000001", 1, '223', '1122333300')
        mkrecord("11000000001", 1, '223', '1122333300')

        #institution #4 records, total = 4; >.5 and <2.0; peer
        mkrecord("11000000002", 1, '222', '1122233300')
        mkrecord("11000000002", 1, '222', '1122233300')
        mkrecord("11000000002", 1, '222', '1122233400')
        mkrecord("11000000002", 1, '222', '1122233300')
        mkrecord("11000000002", 1, '222', '1122233300')

        mkrecord("91000000001", 6, '223', '1222233300')
        call_command('calculate_loan_stats', '2013')

    def tearDown(self):
        Census2010Households.objects.all().delete()
        HMDARecord.objects.all().delete()
        LendingStats.objects.all().delete()

    def test_calculate_loan_stats(self):
        """Case: Institution has no peers but itself in selected metro"""
        institution = Institution.objects.filter(institution_id="11000000001").first()
        metro = Geo.objects.filter(geoid="10000").first()
        peer_list = institution.get_peer_list(metro, False, False)
        self.assertEqual(len(peer_list), 1)
        self.assertEqual(peer_list[0].institution_id, "11000000001")
        
        """Case: Institution has peers in selected metro"""
        institution = Institution.objects.filter(institution_id="91000000001").first()
        metro = Geo.objects.filter(geoid="10000").first()
        peer_list = institution.get_peer_list(metro, False, False)
        self.assertEqual(len(peer_list), 3)
        peer_list_exclude = institution.get_peer_list(metro, True, False)
        self.assertEqual(len(peer_list_exclude), 2)
        peer_list_order = institution.get_peer_list(metro, False, True)
        self.assertEqual(peer_list_order[0].institution_id, "91000000001")
        peer_list_order_exclude = institution.get_peer_list(metro, True, True)
        self.assertEqual(peer_list_order_exclude[0].institution_id, "91000000002")
        self.assertEqual(len(peer_list_exclude), 2) 

    def test_loan_originations_http_user_errors(self):
        #invalid institution_id
        resp = self.client.get(reverse('hmda:volume'), {'metro':'201310000',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'91000000011'})
        self.assertEqual(resp.status_code, 404)

        #invalid metro
        resp = self.client.get(reverse('hmda:volume'), {'metro':'201310011',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'91000000001'})
        self.assertEqual(resp.status_code, 404)

        #invalid metro and institution_id
        resp = self.client.get(reverse('hmda:volume'), {'metro':'201310011',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'91000000011'})
        self.assertEqual(resp.status_code, 404)

    def test_loan_originations_http(self):        
        #valid metro and institution_id
        resp = self.client.get(reverse('hmda:volume'), {'metro':'10000',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'91000000001'})
        self.assertEqual(resp.status_code, 200)

        #no institution_id
        resp = self.client.get(reverse('hmda:volume'), {'metro':'10000',
                                    'action_taken':'1,2,3,4,5'})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue('1122233400' in resp)
        self.assertTrue('1122233300' in resp)
        self.assertEqual(resp['1122233400']['volume'], 5)
        self.assertEqual(resp['1122233400']['num_households'], 1000)  
        self.assertEqual(resp['1122233300']['volume'], 20)
        self.assertEqual(resp['1122233300']['num_households'], 100)         

        #no metro
        resp = self.client.get(reverse('hmda:volume'), {'action_taken':'1,2,3,4,5',
                                    'lender':'91000000001'})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue('1122233400' in resp)
        self.assertTrue('1122233300' in resp)
        self.assertEqual(resp['1122233400']['volume'], 1)
        self.assertEqual(resp['1122233300']['volume'], 4)

        resp = self.client.get(reverse('hmda:volume'), {'neLat':'2',
                                    'neLon':'2',
                                    'swLat':'0',
                                    'swLon':'0',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'91000000001'})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue('1122233300' in resp)
        self.assertEqual(resp['1122233300']['volume'], 4)
        self.assertEqual(resp['1122233300']['num_households'], 100)
        self.assertTrue('1122233400' in resp)
        self.assertEqual(resp['1122233400']['volume'], 1)
        self.assertEqual(resp['1122233400']['num_households'], 1000)

