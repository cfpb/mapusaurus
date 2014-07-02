from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',
    url(r'^(?P<respondant_id>[0-9]+)/', 'respondants.views.respondant'),
    url(r'^search/$', 'respondants.views.search', name='search'),
    url(r'^$', 'respondants.views.index'))


urlpatterns = format_suffix_patterns(urlpatterns)
