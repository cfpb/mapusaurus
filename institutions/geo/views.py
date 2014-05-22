from django.http import HttpResponse

from djgeojson.serializers import Serializer as GeoJSONSerializer

from .models import StateCensusTract


def tracts_by_county(county_fips, state_fips, page_num, page_size):
    """ Provided the FIPS code for a county, return a list of the census tracts
    (including geometry). """

    query = StateCensusTract.objects.filter(
        countyfp=county_fips, statefp=state_fips).order_by('geoid')
    if page_size > 0:
        min_off = page_size * page_num
        max_off = page_size * (page_num + 1)
        query = query[min_off:max_off]
    return GeoJSONSerializer().serialize(query, use_natural_keys=True)


def tracts(request):
    """ Request a list of tracts. """
    county_fips = request.GET.get('county_fips', '')
    state_fips = request.GET.get('state_fips', '')
    try:
        page_num = int(request.GET.get('page_num', '0'))
        page_size = int(request.GET.get('page_size', '0'))
    except ValueError:
        page_num = 0
        page_size = 0   # show all

    serialized_tracts = []

    if county_fips and state_fips:
        serialized_tracts = tracts_by_county(county_fips, state_fips,
                                             page_num, page_size)
    return HttpResponse(serialized_tracts, content_type='application/json')
