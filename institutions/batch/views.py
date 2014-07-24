import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import jsonschema

from censusdata.views import race_summary
from hmda.views import loan_originations


#   JSON Schema for batch request -- used to validate input
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
                'required': ['endpoint'],
                'properties': {
                    'endpoint': {'type': 'string'},
                    'params': {
                        'type': 'object',
                        'additionalProperties': {'type': ['string', 'array']}
                    }
                }
            }
        }
    }
}


# Mapping between requested endpoints (i.e. JS layers) and their handlers
ENDPOINTS = {
    'minority': race_summary,
    'loanVolume': loan_originations
}


@csrf_exempt
def batch(request):
    """This endpoint allows multiple statistical queries to be made in a
    single HTTP request"""
    try:
        body = json.loads(request.body)
        jsonschema.validate(body, BATCH_SCHEMA)
        responses = []
        #   @todo: these should be parallelized
        for request in body['requests']:
            fn = ENDPOINTS[request['endpoint']]
            response = fn(request.get('params', {}))
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
