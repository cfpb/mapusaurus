from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'tracts/?$', 'geo.views.tracts', name='tractsgeojson'),
    url(r'tracts-in', 'geo.views.tracts_in_rect', name='tracts_in_rect')
)
