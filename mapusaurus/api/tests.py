import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound
from django.test import TestCase
from mock import Mock, patch

from utils import use_GET_in, state_county_filter

class ConversionTest(TestCase):

    def test_use_GET_in(self):
        fn, request = Mock(), Mock()
        request.GET.lists.return_value = [('param1', [0]), ('param2', [-1])]

        # Dictionaries become JSON
        fn.return_value = {'a': 1, 'b': 2}
        response = use_GET_in(fn, request)
        self.assertEqual(json.loads(response.content), {'a': 1, 'b': 2})
        self.assertEqual(fn.call_args[0][0], {'param1': [0], 'param2': [-1]})

        # Everything else is unaltered
        fn.return_value = HttpResponseNotFound('Oh noes')
        response = use_GET_in(fn, request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'Oh noes')


class ViewsTests(TestCase):

    def test_api_all_user_errors(self):
        resp = self.client.get(reverse('all'))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('all'), {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'',
                                    'swLon':'-88.225583',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})

        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('all'),   {'neLat':'42.048794',
                                    'neLon':'-87.430698',
                                    'swLat':'41.597775',
                                    'swLon':'',
                                    'year':'2013',
                                    'action_taken':'1,2,3,4,5',
                                    'lender':'736-4045996'})
        self.assertEqual(resp.status_code, 400)

