from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'tracts', 'geo.views.tracts', name='tractsgeojson'),
    )
