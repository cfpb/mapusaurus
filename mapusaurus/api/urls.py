from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^all/', 'api.views.all', name='all'),
)
