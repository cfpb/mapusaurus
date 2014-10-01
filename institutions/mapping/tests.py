from urllib import unquote

from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import Mock, patch

from geo.models import Geo
from mapping.views import make_download_url
from respondants.models import Institution


class ViewTest(TestCase):
    fixtures = ['agency', 'fake_respondents']

    def setUp(self):
        self.respondent = Institution.objects.get(pk=1234567)
        self.metro = Geo.objects.create(
            geoid='12121', geo_type=Geo.METRO_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767)

    def tearDown(self):
        self.metro.delete()

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
        resp = self.client.get(reverse('map'), {'metro': '12121'})
        self.assertTrue('45.4545' in resp.content)
        self.assertTrue('67.6767' in resp.content)
        self.assertTrue('0.11' in resp.content)
        self.assertTrue('0.22' in resp.content)
        self.assertTrue('1.33' in resp.content)
        self.assertTrue('1.44' in resp.content)
        self.assertTrue('MetMetMet' in resp.content)

    def test_make_download_url(self):
        self.assertEqual(None, make_download_url(None, None))
        url = make_download_url(self.respondent, None)
        self.assertTrue('22-333' in url)
        self.assertTrue('1' in url)
        self.assertFalse('msamd' in url)

        url = make_download_url(self.respondent, self.metro)
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
        url = make_download_url(self.respondent, self.metro)
        self.assertFalse('12121' in url)
        self.assertTrue('msamd+IN+("98989","78787")' in unquote(url))

        div1.delete()
        div2.delete() 
