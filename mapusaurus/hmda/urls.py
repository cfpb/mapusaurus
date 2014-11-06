from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^volume/', 'hmda.views.loan_originations_http', name='volume'),
)
