from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'mapping.views.map', {'template':'map.html'}, name='map'),
    url(r'^print/', 'mapping.views.map', {'template' :'print_map.html'}, name='printmap'),
    url(r'^faq/', 'mapping.views.map', {'template' :'faq.html'}, name='faq')
)
