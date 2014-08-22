from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'mapping.views.map', name='map')
)
