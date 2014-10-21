from django.conf.urls import patterns, url
#from mapping.views import map


urlpatterns = patterns(
    '',
    url(r'^$', 'mapping.views.map', {'template': 'map'}, name='map'),
    url(r'^mapbox$', 'mapping.views.map', {'template': 'mapbox'}, name='mapbox')
)
