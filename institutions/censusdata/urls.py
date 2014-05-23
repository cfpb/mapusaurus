from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'race-summary', 'censusdata.views.race_summary', name="race_summary"),
)
