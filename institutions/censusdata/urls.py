from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^race_summary/(?P<northEastLat>-?\d+\.\d{6})/(?P<northEastLon>-?\d+\.\d{6})/(?P<southWestLat>-?\d+\.\d{6})/(?P<southWestLon>-?\d+\.\d{6})/$', 'censusdata.views.race_summary_http', name='race_summary'),
)
