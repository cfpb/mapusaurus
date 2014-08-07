from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'tiles/(?P<zoom>\d+)/(?P<xtile>\d+)/(?P<ytile>\d+)$',
        'geo.views.tile', name='tiles'),
    url(r'search/?$', 'geo.views.search', name='search'),
)
