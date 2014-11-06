from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^tractCentroids/(?P<northEastLat>-?\d+\.\d{6})/(?P<northEastLon>-?\d+\.\d{6})/(?P<southWestLat>-?\d+\.\d{6})/(?P<southWestLon>-?\d+\.\d{6})$', 
        'geo.views.censustract_data', name='censustract_data'),
    url(r'search/?$', 'geo.views.search', name='search'),
)
