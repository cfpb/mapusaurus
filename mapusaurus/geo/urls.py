from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^tractCentroids/(?P<northEastLat>-?\d+\.\d{6})/(?P<northEastLon>-?\d+\.\d{6})/(?P<southWestLat>-?\d+\.\d{6})/(?P<southWestLon>-?\d+\.\d{6})$', 
        'geo.views.tract_centroids_as_json', name='tract_centroids'),
    url(r'search/?$', 'geo.views.search', name='search'),
)
