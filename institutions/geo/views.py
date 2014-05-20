from django.shortcuts import render
from django.http import HttpResponse

from djgeojson.serializers import Serializer as GeoJSONSerializer

from .models import StateCensusTract


def tracts_by_county(county_fips, state_fips):
    """ Provided the FIPS code for a county, return a list of the census tracts
    (including geometry). """

    tracts = list(StateCensusTract.objects.filter(
        countyfp=county_fips, statefp=state_fips))
    return GeoJSONSerializer().serialize(tracts, use_natural_keys=True)


def tracts(request):
    """ Request a list of tracts. """
    county_fips = request.GET.get('county_fips', '')
    state_fips = request.GET.get('state_fips', '')

    serialized_tracts = []

    if county_fips and state_fips:
        serialized_tracts = tracts_by_county(county_fips, state_fips)
    return HttpResponse(serialized_tracts, content_type='application/json')
