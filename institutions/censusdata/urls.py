from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'race-summary', 'censusdata.views.race_summary'),
)
