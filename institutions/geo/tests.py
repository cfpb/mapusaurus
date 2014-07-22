import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from geo.models import Geo


class ViewTest(TestCase):
    fixtures = ['many_tracts']

    def setUp(self):
        """To avoid hand-typing escaped JSON, just generate each here"""
        for tract in Geo.objects.all():
            tract.save()

    def test_tract_tiles(self):
        # lat/lon roughly: 0 to 11
        resp = self.client.get(reverse(
            'geo:tract_tiles',
            kwargs={'zoom': 5, 'xtile': 16, 'ytile': 15}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']),
                         # Doesn't grab the negative tract
                         Geo.objects.all().count() - 1)

        # lat/lon roughly: -6 to -3
        resp = self.client.get(reverse(
            'geo:tract_tiles',
            kwargs={'zoom': 7, 'xtile': 62, 'ytile': 65}))
        resp = json.loads(resp.content)
        self.assertEqual(len(resp['features']), 1)
