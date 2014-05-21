from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse

from .models import Census2010RaceStats


def race_by_county(county_fips, state_fips):
    """ Get race summary statistics by county (specified by FIPS codes). """

    tract_data = Census2010RaceStats.objects.filter(
        geoid__statefp=state_fips, geoid__countyfp=county_fips)
    return tract_data


def race_summary(request):
    """ Get race summary statistics. """
    county_fips = request.GET.get('county_fips', '')
    state_fips = request.GET.get('state_fips', '')

    if county_fips and state_fips:
        tract_data = race_by_county(county_fips, state_fips)
        return HttpResponse(
            serializers.serialize('json', tract_data),
            content_type='application/json')
