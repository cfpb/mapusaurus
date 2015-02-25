from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'search/?$', 'geo.views.search', name='search'),
)
