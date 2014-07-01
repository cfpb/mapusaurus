from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url('^$', 'batch.views.batch', name='batch')
)
