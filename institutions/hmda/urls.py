from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^volume/(?P<northEastLat>-?\d+\.\d{6})/(?P<northEastLon>-?\d+\.\d{6})/(?P<southWestLat>-?\d+\.\d{6})/(?P<southWestLon>-?\d+\.\d{6})/(?P<lender>-?\d+)/(?P<action_taken>-?\d+(,\d+)*)/$', 'hmda.views.loan_originations_http', name='volume'),
)
