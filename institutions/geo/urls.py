from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'tiles/tracts/(?P<zoom>\d+)/(?P<xtile>\d+)/(?P<ytile>\d+)$',
        'geo.views.tract_tile', name='tract_tiles'),
    url(r'search/?$', 'geo.views.search', name='search'),
    url(r'tiles/counties/(?P<zoom>\d+)/(?P<xtile>\d+)/(?P<ytile>\d+)$',
        'geo.views.county_tile', name='county_tiles')
)
