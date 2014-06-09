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
                as_of_year=2014, respondent_id='1111111111',
                agency_code=agency_code, loan_amount_000s=222,
                action_taken=action_taken, statefp='11', countyfp=countyfp)
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

    def test_volume_400(self):
        resp = self.client.get(reverse('hmda:volume'))
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('hmda:volume'),
                               {'county_fips': '1'})
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('hmda:volume'),
                               {'state_fips': '1'})
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('hmda:volume'),
                               {'county_fips': '1', 'state_fips': '3'})
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('hmda:volume'),
                               {'county_fips': '1', 'lender': '3'})
        self.assertEqual(400, resp.status_code)
        resp = self.client.get(reverse('hmda:volume'),
                               {'lender': '1', 'state_fips': '3'})
        self.assertEqual(400, resp.status_code)

    def test_volume(self):
        resp = self.client.get(reverse('hmda:volume'),
                               {'state_fips': '11', 'county_fips': '222',
                                'lender': '11111111111'})
        resp = json.loads(resp.content)
        self.assertEqual(len(resp), 2)
        self.assertTrue('1122233300' in resp)
        self.assertEqual(resp['1122233300']['volume'], 2)
        self.assertEqual(resp['1122233300']['volume_per_100_households'], 2.0)
        self.assertTrue('1122233400' in resp)
        self.assertEqual(resp['1122233400']['volume'], 1)
        self.assertEqual(resp['1122233400']['volume_per_100_households'], 0.1)
