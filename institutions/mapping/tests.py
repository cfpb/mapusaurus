from urllib import unquote

from django.core.urlresolvers import reverse
from django.test import TestCase

from geo.models import Geo
from hmda.models import HMDARecord
from mapping.views import calculate_median_loans, make_download_url
from respondants.models import Agency, Institution, ZipcodeCityState


class ViewTest(TestCase):
    fixtures = ['agency']

    def setUp(self):
        self.zip_code = ZipcodeCityState.objects.create(
            zip_code=11111, city='Somewhere', state='NE')
        agency = Agency.objects.get(pk=1)
        self.respondent = Institution.objects.create(
            year=1970, ffiec_id='22-333', agency=agency, tax_id='taxtax',
            name='Some Bank', mailing_address='123 Avenue St.',
            zip_code=self.zip_code, rssd_id='Other ID')

    def tearDown(self):
        self.respondent.delete()
        self.zip_code.delete()

    def test_home(self):
        resp = self.client.get(reverse('map'))
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('map'), {'some': 'thing'})
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('map'), {'lender': 'thing'})
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('map'), {'lender': '123456789'})
        self.assertFalse('lender-info' in resp.content)

        resp = self.client.get(reverse('map'), {'lender': '122-333'})
        self.assertTrue('lender-info' in resp.content)
        self.assertTrue('Some Bank' in resp.content)
        self.assertTrue('123 Avenue St.' in resp.content)
        self.assertTrue('1970' in resp.content)
        self.assertTrue('11111' in resp.content)
        self.assertTrue('Somewhere' in resp.content)
        self.assertTrue('NE' in resp.content)

    def test_center(self):
        metro = Geo.objects.create(
            geoid='12121', geo_type=Geo.METRO_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767)
        resp = self.client.get(reverse('map'), {'metro': '12121'})
        self.assertTrue('45.4545' in resp.content)
        self.assertTrue('67.6767' in resp.content)
        self.assertTrue('0.11' in resp.content)
        self.assertTrue('0.22' in resp.content)
        self.assertTrue('1.33' in resp.content)
        self.assertTrue('1.44' in resp.content)
        self.assertTrue('MetMetMet' in resp.content)
        metro.delete()

    def test_make_download_url(self):
        self.assertEqual(None, make_download_url(None, None))
        url = make_download_url(self.respondent, None)
        self.assertTrue('22-333' in url)
        self.assertTrue('1' in url)
        self.assertFalse('msamd' in url)

        metro = Geo.objects.create(
            geoid='12121', geo_type=Geo.METRO_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767)
        url = make_download_url(self.respondent, metro)
        self.assertTrue('msamd="12121"' in unquote(url))

        div1 = Geo.objects.create(
            geoid='123123', geo_type=Geo.METDIV_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767, cbsa='12121', metdiv='98989')
        div2 = Geo.objects.create(
            geoid='123124', geo_type=Geo.METDIV_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767, cbsa='12121', metdiv='78787')
        url = make_download_url(self.respondent, metro)
        self.assertFalse('12121' in url)
        self.assertTrue('msamd+IN+("98989","78787")' in unquote(url))

        div1.delete()
        div2.delete()
        metro.delete()

    def test_calculate_median_loans(self):
        tract_params = {
            'geo_type': Geo.TRACT_TYPE, 'minlat': 0.11, 'minlon': 0.22,
            'maxlat': 1.33, 'maxlon': 1.44, 'centlat': 45.4545,
            'centlon': 67.67, 'geom': "MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))"}
        city_tract1 = Geo.objects.create(name='City Tract 1', cbsa='99999',
                                         geoid='11111111', **tract_params)
        city_tract2 = Geo.objects.create(name='City Tract 2', cbsa='99999',
                                         geoid='11111112', **tract_params)
        # also create a tract with no loans
        city_tract3 = Geo.objects.create(name='City Tract 3', cbsa='99999',
                                         geoid='11111113', **tract_params)

        non_city_tract1 = Geo.objects.create(name='Non-City Tract 4',
                                             geoid='11111114', **tract_params)
        non_city_tract2 = Geo.objects.create(name='Non-City Tract 5',
                                             geoid='11111115', **tract_params)
        del tract_params['geo_type']
        metro = Geo(name='City', geoid='99999', geo_type=Geo.METRO_TYPE,
                    **tract_params)
        hmda_params = {
            'as_of_year': 2010, 'respondent_id': self.respondent.ffiec_id,
            'agency_code': str(self.respondent.agency_id),
            'loan_amount_000s': 100, 'action_taken': 1, 'statefp': '11',
            'countyfp': '111'}
        hmdas = []
        hmdas.append(HMDARecord.objects.create(
            geoid=city_tract1, **hmda_params))
        for i in range(5):
            hmdas.append(HMDARecord.objects.create(
                geoid=city_tract2, **hmda_params))
        for i in range(11):
            hmdas.append(HMDARecord.objects.create(
                geoid=non_city_tract1, **hmda_params))
        for i in range(8):
            hmdas.append(HMDARecord.objects.create(
                geoid=non_city_tract2, **hmda_params))

        # 1 in tract 1, 5 in 2, 0 in 3;                     avg: 2, med: 1
        self.assertEqual(1, calculate_median_loans(self.respondent, metro))
        # 1 in tract 1, 5 in 2, 0 in 3, 11 in 4, 8 in 5;    avg: 6, med: 5
        self.assertEqual(5, calculate_median_loans(self.respondent, None))

        hmda_params['respondent_id'] = 'other'
        # these should not affect the results, since they are another lender
        for i in range(3):
            hmdas.append(HMDARecord.objects.create(
                geoid=city_tract2, **hmda_params))
        self.assertEqual(1, calculate_median_loans(self.respondent, metro))
        self.assertEqual(5, calculate_median_loans(self.respondent, None))

        for hmda in hmdas:
            hmda.delete()
        city_tract1.delete()
        city_tract2.delete()
        city_tract3.delete()
        non_city_tract1.delete()
        non_city_tract2.delete()
        metro.delete()
