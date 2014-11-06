from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',
    url(r'^(?P<agency_id>[0-9])(?P<respondent>[0-9-]{10})/metro-search/?$',
        'respondents.views.select_metro', name='select_metro'),
    url(r'^search/$', 'respondents.views.search_results',
        name='search_results'),
    url(r'^$', 'respondents.views.search_home', name='search_home'),
	url(r'^respondent/(?P<agency_id>[0-9])(?P<respondent>[0-9-]{10})',
		'respondents.views.respondent', name='respondent_profile')
	)

urlpatterns = format_suffix_patterns(urlpatterns)
