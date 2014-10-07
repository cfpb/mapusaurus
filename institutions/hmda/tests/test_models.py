from django.test import TestCase

from hmda.models import HMDARecord


class HMDARecordTest(TestCase):
    fixtures = ['many_tracts']

    def test_auto_fields(self):
        record = HMDARecord(
            as_of_year=2014, respondent_id='0123456789', agency_code='3',
            loan_type=1, property_type=1, loan_purpose=1, owner_occupancy=1,
            loan_amount_000s=55, preapproval='1', action_taken=1,
            msamd='01234', state_code='11', county_code='222',
            census_tract_number ='01234', applicant_ethnicity='1',
            co_applicant_ethnicity='1', applicant_race_1='1', co_applicant_race_1='1',
            applicant_sex='1', co_applicant_sex='1', applicant_income_000s='1000',
            purchaser_type='1', rate_spread='0123', hoepa_status='1', lien_status='1',
            sequence_number='1', population='1', minority_population='1',
            ffieic_median_family_income='1000', tract_to_msamd_income='1000',
            number_of_owner_occupied_units='1', number_of_1_to_4_family_units='1',
            application_date_indicator=1)
        record.geoid_id = '11222333000'
        record.save()
        self.assertEqual(record.lender, '30123456789')
        record.delete()

        record = HMDARecord(
            as_of_year=2014, respondent_id='01-345-789', agency_code='2',
            loan_type=1, property_type=1, loan_purpose=1, owner_occupancy=1,
            loan_amount_000s=55, preapproval='1', action_taken=1,
            msamd='01234', state_code='11', county_code='222',
            census_tract_number ='01234', applicant_ethnicity='1',
            co_applicant_ethnicity='1', applicant_race_1='1', co_applicant_race_1='1',
            applicant_sex='1', co_applicant_sex='1', applicant_income_000s='1000',
            purchaser_type='1', rate_spread='0123', hoepa_status='1', lien_status='1',
            sequence_number='1', population='1', minority_population='1',
            ffieic_median_family_income='1000', tract_to_msamd_income='1000',
            number_of_owner_occupied_units='1', number_of_1_to_4_family_units='1',
            application_date_indicator=1)
        record.auto_fields()
        self.assertEqual(record.lender, '201-345-789')
