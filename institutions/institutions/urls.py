from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url='/institutions/')),
    url(r'^batch', include('batch.urls')),
    url(r'^institutions/', include('respondants.urls',
                                   namespace='respondants')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^shapes/', include('geo.urls', namespace='geo')),
    url(r'^hmda/', include('hmda.urls', namespace='hmda')),
    url(r'^map/', include('mapping.urls')),
    url(r'^census/', include('censusdata.urls', namespace='censusdata'))
)
