from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^all/', 'api.views.all', name='all'),
    url(r'^hmda/', 'api.views.hmda', name='hmda'),
    url(r'^census/', 'api.views.census', name='census'),
    url(r'^tables/', 'api.views.tables', name='tables'),
    url(r'^tables_csv/', 'api.views.tables_csv', name='tables_csv'),
    url(r'^msas/', 'api.views.msas', name='msas'),
    url(r'^tractCentroids/', 'api.views.tractCentroids', name='tractCentroids'),
    url(r'^branchLocations/', 'api.views.branch_locations', name='branchLocations'),
)
