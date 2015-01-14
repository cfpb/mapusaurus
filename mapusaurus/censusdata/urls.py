from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^race_summary/', 'censusdata.views.race_summary_http', name='race_summary'),
    url(r'^race_summary_csv/', 'censusdata.views.race_summary_csv', name='race_summary_csv'),
)
