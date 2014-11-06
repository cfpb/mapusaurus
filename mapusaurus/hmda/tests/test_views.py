import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from censusdata.models import Census2010Households
from hmda.models import HMDARecord


class ViewsTest(TestCase):
    fixtures = ['dummy_tracts']

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

        def mkrecord(action_taken, agency_code, countyfp, geoid):
            record = HMDARecord(
                as_of_year=2014, respondent_id='1111111111', agency_code=agency_code,
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
        
            record.geoid_id = geoid
            record.save()

        mkrecord(1, '1', '222', '1122233300')
        mkrecord(1, '1', '222', '1122233300')
        mkrecord(1, '1', '222', '1122233400')
        mkrecord(8, '1', '222', '1122233300')
        mkrecord(1, '2', '222', '1122233300')
        mkrecord(1, '1', '223', '1122333300')

    def tearDown(self):
        Census2010Households.objects.all().delete()
        HMDARecord.objects.all().delete()


