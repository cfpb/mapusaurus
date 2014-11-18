from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'mapping.views.map', name='map'),
    url(r'^print/', 'mapping.views.printmap', name='printmap')
)
