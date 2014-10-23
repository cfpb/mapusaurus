from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^tractCentroids/(?P<northEastLat>-?\d+\.\d{6})/(?P<northEastLon>-?\d+\.\d{6})/(?P<southWestLat>-?\d+\.\d{6})/(?P<southWestLon>-?\d+\.\d{6})$', 
        'geo.views.tractCentroids', name='getCensusTracts'),
    url(r'^tiles/(?P<zoom>\d+)/(?P<xtile>\d+)/(?P<ytile>\d+)$',
        'geo.views.tile', name='tiles'),
    url(r'^topotiles/(?P<zoom>\d+)/(?P<xtile>\d+)/(?P<ytile>\d+)$',
        'geo.views.topotile', name='topotiles'),
    url(r'search/?$', 'geo.views.search', name='search'),
)
