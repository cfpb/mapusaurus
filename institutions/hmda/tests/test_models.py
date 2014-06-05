from django.test import TestCase

from hmda.models import HMDARecord


class HMDARecordTest(TestCase):
    fixtures = ['many_tracts']

    def test_auto_fields(self):
        record = HMDARecord(
            as_of_year=2014, respondent_id='0123456789', agency_code='3',
            loan_amount_000s=55, action_taken=1, statefp='11', countyfp='222')
        record.geoid_id = '11222333000'
        record.save()
        self.assertEqual(record.lender, '30123456789')
        record.delete()

        record = HMDARecord(
            as_of_year=2014, respondent_id='01-345-789', agency_code='2',
            loan_amount_000s=55, action_taken=1, statefp='ST',
            countyfp='COU')
        record.auto_fields()
        self.assertEqual(record.lender, '201-345-789')
