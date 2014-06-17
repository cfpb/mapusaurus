import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import jsonschema

from censusdata.views import race_summary
from hmda.views import loan_originations


BATCH_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['requests'],
    'properties': {
        'requests': {
            'type': 'array',
            'minItems': 1,
            'additionalItems': False,
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['endpoint', 'params'],
                'properties': {
                    'endpoint': {'type': 'string'},
                    'params': {
                        'type': 'object',
                        'additionalProperties': {'type': 'string'}
                    }
                }
            }
        }
    }
}


ENDPOINTS = {
    'minority': race_summary,
    'loanVolume': loan_originations
}


@csrf_exempt
def batch(request):
    """ As the query may be complicated, we use an json-encoded post body """
    try:
        body = json.loads(request.body)
        jsonschema.validate(body, BATCH_SCHEMA)
        responses = []
        for request in body['requests']:
            fn = ENDPOINTS[request['endpoint']]
            response = fn(request['params'])
            if isinstance(response, dict):
                responses.append(response)
            else:
                return response     # whole request errors
        return HttpResponse(json.dumps({'responses': responses}),
                            content_type='application/json')
    except KeyError:
        return HttpResponseBadRequest("invalid endpoint")
    except ValueError:
        return HttpResponseBadRequest("invalid format")
    except jsonschema.ValidationError:
        return HttpResponseBadRequest("JSON is invalid")
