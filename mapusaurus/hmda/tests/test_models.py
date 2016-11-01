from django.test import TestCase

from hmda.models import HMDARecord


class HMDARecordTest(TestCase):
    fixtures = ['fake_respondents', 'agency', 'many_tracts']

    def test_auto_fields(self):
        record = HMDARecord(
            as_of_year=2015, respondent_id='22-333', agency_code='9',
            loan_type=1, property_type=1, loan_purpose=1, owner_occupancy=1,
            loan_amount_000s=55, preapproval='1', action_taken=1,
            msamd='01234', statefp='11', countyfp='222',
            census_tract_number ='01234', applicant_ethnicity='1',
            co_applicant_ethnicity='1', applicant_race_1='1', co_applicant_race_1='1',
            applicant_sex='1', co_applicant_sex='1', applicant_income_000s='1000',
            purchaser_type='1', rate_spread='0123', hoepa_status='1', lien_status='1',
            sequence_number='1', population='1', minority_population='1',
            ffieic_median_family_income='1000', tract_to_msamd_income='1000',
            number_of_owner_occupied_units='1', number_of_1_to_4_family_units='1',
            application_date_indicator=1)
        record.geo_id = '11222333000'
        record.institution_id='922-333'
        record.save()
        self.assertEqual(record.institution_id, '922-333')
        record.delete()

        record = HMDARecord(
            as_of_year=2015, respondent_id='22-333', agency_code='9',
            loan_type=1, property_type=1, loan_purpose=1, owner_occupancy=1,
            loan_amount_000s=55, preapproval='1', action_taken=1,
            msamd='01234', statefp='11', countyfp='222',
            census_tract_number ='01234', applicant_ethnicity='1',
            co_applicant_ethnicity='1', applicant_race_1='1', co_applicant_race_1='1',
            applicant_sex='1', co_applicant_sex='1', applicant_income_000s='1000',
            purchaser_type='1', rate_spread='0123', hoepa_status='1', lien_status='1',
            sequence_number='1', population='1', minority_population='1',
            ffieic_median_family_income='1000', tract_to_msamd_income='1000',
            number_of_owner_occupied_units='1', number_of_1_to_4_family_units='1',
            application_date_indicator=1)
        record.geo_id='11222333000'
        record.institution_id='922-333'
        self.assertEqual(record.institution_id, '922-333')
