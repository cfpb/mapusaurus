import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound
from django.test import TestCase
from mock import Mock, patch

from batch import views
from batch.conversions import use_GET_in


class ConversionTest(TestCase):
    """Tests batch.conversions"""
    def test_use_GET_in(self):
        fn, request = Mock(), Mock()
        request.GET = {'param1': 0, 'param2': -1}

        # Dictionaries become JSON
        fn.return_value = {'a': 1, 'b': 2}
        response = use_GET_in(fn, request)
        self.assertEqual(json.loads(response.content), {'a': 1, 'b': 2})
        self.assertEqual(fn.call_args[0][0], {'param1': 0, 'param2': -1})

        # Everything else is unaltered
        fn.return_value = HttpResponseNotFound('Oh noes')
        response = use_GET_in(fn, request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'Oh noes')


class ViewsTests(TestCase):
    """Tests batch.views"""
    def test_batch_user_errors(self):
        resp = self.client.post(reverse('batch'),
                                content_type='application/json',
                                data='not json')
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post(reverse('batch'),
                                content_type='application/json',
                                data='[]')
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post(reverse('batch'),
                                content_type='application/json',
                                data='{"thing": 5')
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post(reverse('batch'),
                                content_type='application/json',
                                data='{"requests": [{"endpoint": "xxx"}]')
        self.assertEqual(resp.status_code, 400)

    @patch.dict('batch.views.ENDPOINTS', other=Mock())
    def test_batch_user(self):
        views.ENDPOINTS['other'].return_value = {'some': 3}
        data = {"requests": [
            {"endpoint": "other"},
            {"endpoint": "other", "params": {"a": "1"}},
            {"endpoint": "other", "params": {"a": "5", "b": "8"}}
        ]}
        resp = self.client.post(reverse('batch'),
                                content_type='application/json',
                                data=json.dumps(data))
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertEqual(resp['responses'], [{'some': 3}]*3)
        args = [call[0][0] for call in
                views.ENDPOINTS['other'].call_args_list]
        self.assertEqual(3, len(args))
        args1, args2, args3 = args
        self.assertEqual(args1, {})
        self.assertEqual(args2, {'a': '1'})
        self.assertEqual(args3, {'a': '5', 'b': '8'})
