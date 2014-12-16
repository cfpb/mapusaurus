from django.test import TestCase
from mock import Mock

from geo.models import Geo
from hmda.management.commands.calculate_loan_stats import (
     calculate_median_loans, Command)
from hmda.models import HMDARecord, LendingStats
from respondents.models import Institution


class PrecalcTest(TestCase):
    fixtures = ['agency', 'fake_respondents']

    def setUp(self):
        self.respondent = Institution.objects.get(pk=1234567)
        tract_params = {
            'geo_type': Geo.TRACT_TYPE, 'minlat': 0.11, 'minlon': 0.22,
            'maxlat': 1.33, 'maxlon': 1.44, 'centlat': 45.4545,
            'centlon': 67.67, 'geom': "MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))"}
        self.city_tract1 = Geo.objects.create(
            name='City Tract 1', cbsa='99999', geoid='11111111',
            **tract_params)
        self.city_tract2 = Geo.objects.create(
            name='City Tract 2', cbsa='99999', geoid='11111112',
            **tract_params)
        self.city_tract3 = Geo.objects.create(
            name='City Tract 3', cbsa='99999', geoid='11111113',
            **tract_params)
        # also create a tract with no loans
        self.city_tract4 = Geo.objects.create(
            name='City Tract 4', cbsa='99999', geoid='11111114',
            **tract_params)

        self.non_city_tract1 = Geo.objects.create(
            name='Non-City Tract 5', geoid='11111115', **tract_params)
        self.non_city_tract2 = Geo.objects.create(
            name='Non-City Tract 6', geoid='11111116', **tract_params)
        del tract_params['geo_type']
        self.metro = Geo.objects.create(
            name='City', geoid='99999', geo_type=Geo.METRO_TYPE,
            **tract_params)
        

        hmda_params = {
            'as_of_year': 2010, 'respondent_id': self.respondent.respondent_id,
            'agency_code': str(self.respondent.agency_id), 'loan_type': 1,
            'property_type': 1, 'loan_purpose': 1, 'owner_occupancy': 1,
            'loan_amount_000s': 100, 'preapproval': '1', 'action_taken': 1, 
            'msamd': '01234', 'statefp': '11', 'countyfp': '111',
            'census_tract_number': '01234', 'applicant_ethnicity': '1',
            'co_applicant_ethnicity': '1', 'applicant_race_1':'1', 'co_applicant_race_1':'1',
            'applicant_sex': '1', 'co_applicant_sex': '1', 'applicant_income_000s': '1000',
            'purchaser_type': '1', 'rate_spread': '0123', 'hoepa_status': '1', 'lien_status': '1',
            'sequence_number': '1', 'population': '1', 'minority_population': '1',
            'ffieic_median_family_income' :'1000', 'tract_to_msamd_income': '1000',
            'number_of_owner_occupied_units': '1', 'number_of_1_to_4_family_units': '1',
            'application_date_indicator':1}
        self.hmdas = []
        self.hmdas.append(HMDARecord.objects.create(
            geoid=self.city_tract1, **hmda_params))
        for i in range(3):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.city_tract2, **hmda_params))
        for i in range(8):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.city_tract3, **hmda_params))
        for i in range(7):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.non_city_tract1, **hmda_params))
        for i in range(11):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.non_city_tract2, **hmda_params))

        hmda_params['respondent_id'] = 'other'
        # these should not affect the results, since they are another lender
        for i in range(3):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.city_tract2, **hmda_params))

    def tearDown(self):
        for hmda in self.hmdas:
            hmda.delete()
        self.city_tract1.delete()
        self.city_tract2.delete()
        self.city_tract3.delete()
        self.city_tract4.delete()
        self.non_city_tract1.delete()
        self.non_city_tract2.delete()
        self.metro.delete()

    def test_calculate_median_loans(self):
        lender_id = str(self.respondent.agency_id) + self.respondent.respondent_id
        # 1 in tract 1, 3 in 2, 8 in 3, 0 in 4;             avg: 4, med: 3
        self.assertEqual(3, calculate_median_loans(lender_id, self.metro))
        # 1 in tract 1, 3 in 2, 8 in 3, 0 in 4; 7 in 5, 16 in 6; avg:6, med:7
        self.assertEqual(7, calculate_median_loans(lender_id, None))

    def test_saves_stats(self):
        lender_id = str(self.respondent.agency_id) + self.respondent.respondent_id
        command = Command()
        command.stdout = Mock()
        command.handle()

        found = False
        for stats in LendingStats.objects.all():
            if stats.geoid_id == '99999' and stats.lender == lender_id:
                found = True
                self.assertEqual(stats.median_per_tract, 3)
        self.assertTrue(found)
