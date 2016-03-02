from urllib import unquote

from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import Mock, patch

from hmda.models import Year
from geo.models import Geo
from mapping.views import lookup_median, make_download_url
from respondents.models import Institution


class ViewTest(TestCase):
    fixtures = ['agency', 'fake_respondents']

    def setUp(self):
        self.respondent = Institution.objects.get(institution_id="922-333")
        self.metro = Geo.objects.create(
            geoid='12121', cbsa='12345', geo_type=Geo.METRO_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767, year='2012')
        self.year = Year.objects.create(hmda_year=2012, census_year=2010, geo_year=2011)

    def tearDown(self):
        self.metro.delete()

    def test_home(self):
        resp = self.client.get(reverse('map'))
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('map'), {'some': 'thing'})
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('map'), {'lender': 'thing'})
        self.assertFalse('lender-info' in resp.content)
        resp = self.client.get(reverse('map'), {'lender': '"922-33"89'})
        self.assertFalse('lender-info' in resp.content)

        resp = self.client.get(reverse('map'), {'lender': '922-333'})
        self.assertTrue('lender-info' in resp.content)
        self.assertTrue('Some Bank' in resp.content)
        self.assertTrue('1970' in resp.content)
        self.assertTrue('Somewhere' in resp.content)
        self.assertTrue('NE' in resp.content)

    def test_center(self):
        resp = self.client.get(reverse('map'), {'metro': '12121'})
        self.assertTrue('45.4545' in resp.content)
        self.assertTrue('67.6767' in resp.content)
        self.assertTrue('10' in resp.content)
        self.assertTrue('12' in resp.content)
        self.assertTrue('MetMetMet' in resp.content)
        self.assertTrue('year' in resp.content)

    def test_make_download_url(self):
        self.assertEqual("https://api.consumerfinance.gov/data/hmda/slice/hmda_lar.csv?%24where=&%24limit=0", make_download_url(None, None))
        url = make_download_url(self.respondent, None)
        self.assertTrue('22-333' in url)
        self.assertTrue('1' in url)
        self.assertFalse('msamd' in url)

        url = make_download_url(self.respondent, self.metro)
        self.assertTrue('msamd="12345"' in unquote(url))

        div1 = Geo.objects.create(
            geoid='123123', geo_type=Geo.METDIV_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767, cbsa='12345', metdiv='98989', year='2012')
        div2 = Geo.objects.create(
            geoid='123124', geo_type=Geo.METDIV_TYPE, name='MetMetMet',
            geom="MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))", minlat=0.11,
            minlon=0.22, maxlat=1.33, maxlon=1.44, centlat=45.4545,
            centlon=67.6767, cbsa='12345', metdiv='78787', year='2012')
        
        url = make_download_url(self.respondent, self.metro)
        self.assertFalse('12121' in url)
        self.assertTrue('msamd+IN+("78787","98989")' in unquote(url) or 'msamd+IN+("98989","78787")' in unquote(url))

        div1.delete()
        div2.delete()

    @patch('mapping.views.LendingStats')
    @patch('mapping.views.calculate_median_loans')
    def test_lookup_median(self, calc, LendingStats):
        lender_str = self.respondent.institution_id
        # No lender
        self.assertEqual(None, lookup_median(None, None))
        # All of the US
        lookup_median(self.respondent, None)
        self.assertEqual(calc.call_args[0], (lender_str, None))
        # Entry in the db
        mock_obj = Mock()
        mock_obj.lar_median = 9898
        LendingStats.objects.filter.return_value.first.return_value = mock_obj
        self.assertEqual(9898, lookup_median(self.respondent, self.metro))
        # No entry in db
        LendingStats.objects.filter.return_value.first.return_value = None
        lookup_median(self.respondent, self.metro)
        self.assertEqual(calc.call_args[0], (lender_str, self.metro))
