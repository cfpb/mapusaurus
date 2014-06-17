from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import select_template


def home(request):
    context = RequestContext(request, {})
    template = select_template(['custom-index.html', 'index.html'])
    return HttpResponse(template.render(context))
