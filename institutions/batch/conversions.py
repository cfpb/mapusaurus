import json

from django.http import HttpResponse


def use_GET_in(fn, request):
    """Pass the request's GET dictionary in to fn. If the response is not a
    dictionary, we know something went wrong, so just pass it back. Otherwise,
    convert the dictionary into a json response."""
    get = {}
    for key, value in request.GET.lists():
        get[key] = value
    response = fn(get)
    if isinstance(response, dict):
        return HttpResponse(json.dumps(response),
                            content_type='application/json')
    else:
        return response
