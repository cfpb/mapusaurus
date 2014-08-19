from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',
    url(r'^(?P<agency_id>[0-9])(?P<respondent>[0-9-]{10})/metro/?$',
        'respondants.views.select_metro', name='select_metro'),
    url(r'^search/$', 'respondants.views.search_results',
        name='search_results'),
    url(r'^$', 'respondants.views.search_home', name='search_home'),
	url(r'^respondant/(?P<agency_id>[0-9])(?P<respondent>[0-9-]{10})',
		'respondants.views.respondant', name='respondant_profile')
	)

urlpatterns = format_suffix_patterns(urlpatterns)
