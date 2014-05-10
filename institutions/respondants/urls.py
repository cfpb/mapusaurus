from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'(?P<respondant_id>[0-9]+)', 'respondants.views.respondant'),
    url(r'search', 'respondants.views.search'),
    url(r'', 'respondants.views.index'))
