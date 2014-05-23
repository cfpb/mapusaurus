from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse

from djgeojson.serializers import Serializer as GeoJSONSerializer

from .models import StateCensusTract


def tracts(request):
    """ Request a list of tracts by provided county/state fips. """
    county_fips = request.GET.get('county_fips', '')
    state_fips = request.GET.get('state_fips', '')

    tracts = StateCensusTract.objects.filter(
        countyfp=county_fips, statefp=state_fips).order_by('geoid')

    if 'page_num' in request.GET:
        page_size = 1000
        if request.GET.get('page_size', '').isdigit():
            page_size = int(request.GET['page_size'])

        pager = Paginator(tracts, page_size)
        try:
            tracts = pager.page(request.GET.get('page_num')).object_list
        except PageNotAnInteger:
            tracts = pager.page(1).object_list
        except EmptyPage:
            tracts = []

    return HttpResponse(
        GeoJSONSerializer().serialize(tracts, use_natural_keys=True),
        content_type='application/json')
