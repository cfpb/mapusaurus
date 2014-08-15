from django.core.urlresolvers import reverse
from django.test import TestCase

from geo.models import Geo
from mapping.views import make_download_url
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
        resp = self.client.get(reverse('home'))
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('home'), {'some': 'thing'})
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('home'), {'lender': 'thing'})
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('home'), {'lender': '123456789'})
        self.assertFalse('lender-info' in resp.content)

        resp = self.client.get(reverse('home'), {'lender': '122-333'})
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
        resp = self.client.get(reverse('home'), {'metro': '12121'})
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
        self.assertTrue('msamd-1=12121' in url)

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
        self.assertTrue('msamd-1=98989' in url)
        self.assertTrue('msamd-2=78787' in url)

        div1.delete()
        div2.delete()
        metro.delete()
