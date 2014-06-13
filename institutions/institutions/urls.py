from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'mapping.views.home', name='home'),
    url(r'^batch$', 'mapping.views.batch', name='batch'),
    url(r'^institutions/', include('respondants.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^shapes/', include('geo.urls', namespace='geo')),
    url(r'^hmda/', include('hmda.urls', namespace='hmda')),
    url(r'^census/', include('censusdata.urls', namespace='censusdata'))
)
