from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'race-summary', 'censusdata.views.race_summary_http',
        name="race_summary"),
    url(
        r'statistics',
        'censusdata.views.statistics_retriever', name="statistics"),
)
