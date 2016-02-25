from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',
    url(r'^(?P<year>[0-9]{4})/(?P<agency_id>[0-9])(?P<respondent>[0-9-]{10})/metro/?$',
        'respondents.views.select_metro', name='select_metro'),
    url(r'^search/$', 'respondents.views.search_results',
        name='search_results'),
    url(r'^$', 'respondents.views.search_home', name='search_home'),
	url(r'^respondent/(?P<year>[0-9]{4})(?P<agency_id>[0-9])(?P<respondent>[0-9-]{10})',
		'respondents.views.respondent', name='respondent_profile'),
    url(r'^branchLocations/(?P<northEastLat>-?\d+\.\d{6})/(?P<northEastLon>-?\d+\.\d{6})/(?P<southWestLat>-?\d+\.\d{6})/(?P<southWestLon>-?\d+\.\d{6})$',
        'respondents.views.branch_locations_as_json', name='branch_locations'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
