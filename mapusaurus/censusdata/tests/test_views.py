import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from respondents.models import Institution
from geo.models import Geo
from censusdata.models import Census2010RaceStats,Census2010Households
from hmda.models import HMDARecord, LendingStats

class ViewsTest(TestCase):
    fixtures = ['agency', 'fake_respondents', 'dummy_tracts', 'fake_msa']

    def setUp(self):

        def mkrecord_household(geoid, total):
            record = Census2010Households(geoid_id=geoid,total=total,
                total_family=0,husband_wife=0,total_family_other=0,male_no_wife=0,female_no_husband=0,total_nonfamily=0, living_alone=0,not_living_alone=0)
            record.save()

        def mkrecord_hmda(institution_id, action_taken, countyfp, geoid):
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

        stats = Census2010RaceStats(
            total_pop=10, hispanic=1, non_hisp_white_only=2,
            non_hisp_black_only=4, non_hisp_asian_only=5)
        stats.geoid_id = '1122233300'
        stats.save()
        mkrecord_hmda("91000000001", 1, '222', stats.geoid_id)
        mkrecord_household(stats.geoid_id,99)

        stats = Census2010RaceStats(
            total_pop=20, hispanic=2, non_hisp_white_only=1,
            non_hisp_black_only=5, non_hisp_asian_only=4)
        stats.geoid_id = '1122233400'
        stats.save()
        mkrecord_hmda("91000000001", 1, '222', stats.geoid_id)
        mkrecord_household(stats.geoid_id,1237)

        stats = Census2010RaceStats(
            total_pop=100, hispanic=10, non_hisp_white_only=20,
            non_hisp_black_only=30, non_hisp_asian_only=4)
        stats.geoid_id = '1122333300'
        stats.save()
        mkrecord_household(stats.geoid_id,99)

        stats = Census2010RaceStats(
            total_pop=100, hispanic=0, non_hisp_white_only=0,
            non_hisp_black_only=0, non_hisp_asian_only=7)
        stats.geoid_id = '1222233300'
        stats.save()
        mkrecord_household(stats.geoid_id,99)
        lendstats = LendingStats(
            geo_id='10000', institution_id="736-4045996",
            lar_median=3, lar_count=4,
            fha_count=2, fha_bucket=2)
        lendstats.save()


    def tearDown(self):
        Census2010RaceStats.objects.all().delete()


    def test_race_summary(self):
        resp = self.client.get(reverse('censusdata:race_summary'),
                               {'neLat':'1',
                                    'neLon':'1',
                                    'swLat':'0',
                                    'swLon':'0',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        resp = json.loads(resp.content)
        self.assertEqual(len(resp), 4)
        self.assertTrue('1122233300' in resp)
        self.assertEqual(resp['1122233300']['total_pop'], 10)
        self.assertEqual(resp['1122233300']['hispanic'], 1)
        self.assertEqual(resp['1122233300']['non_hisp_white_only'], 2)
        self.assertEqual(resp['1122233300']['non_hisp_black_only'], 4)
        self.assertEqual(resp['1122233300']['non_hisp_asian_only'], 5)
        self.assertEqual(resp['1122233300']['hispanic_perc'], .1)
        self.assertEqual(resp['1122233300']['non_hisp_white_only_perc'], .2)
        self.assertEqual(resp['1122233300']['non_hisp_black_only_perc'], .4)
        self.assertEqual(resp['1122233300']['non_hisp_asian_only_perc'], .5)
        self.assertTrue('1122233400' in resp)
        self.assertEqual(resp['1122233400']['total_pop'], 20)
        self.assertEqual(resp['1122233400']['hispanic'], 2)
        self.assertEqual(resp['1122233400']['non_hisp_white_only'], 1)
        self.assertEqual(resp['1122233400']['non_hisp_black_only'], 5)
        self.assertEqual(resp['1122233400']['non_hisp_asian_only'], 4)
        self.assertEqual(resp['1122233400']['hispanic_perc'], .1)
        self.assertEqual(resp['1122233400']['non_hisp_white_only_perc'], .05)
        self.assertEqual(resp['1122233400']['non_hisp_black_only_perc'], .25)
        self.assertEqual(resp['1122233400']['non_hisp_asian_only_perc'], .2)

    def test_race_summary_csv(self):
        resp = self.client.get(reverse('censusdata:race_summary_csv'))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(reverse('censusdata:race_summary_csv'),
            {'metro':'10000', 'lender':'91000000001', 'action_taken':'1,2,3,4'})
        resp = resp.content
        self.assertTrue('1122233300' in resp)
        self.assertTrue('1122233400' in resp)
        self.assertTrue('1122333300' in resp)
        self.assertTrue('1237' in resp)






