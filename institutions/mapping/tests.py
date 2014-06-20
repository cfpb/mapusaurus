from django.core.urlresolvers import reverse
from django.test import TestCase

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
