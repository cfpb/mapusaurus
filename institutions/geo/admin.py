from django.contrib.gis import admin
from models import Geo

# Register your models here.

class GeoAdmin(admin.GeoModelAdmin):
    list_display = ['geoid', 'geo_type', 'name', 'state', 'county', 'tract', 'csa', 'cbsa', 'metdiv', 'centlat', 'centlon']

    search_fields = ['name']

    readonly_fields = (
        'geoid',
        'geo_type',
        'name',
        'state',
        'county',
        'tract',
        'csa',
        'cbsa',
        'metdiv',
        'minlat',
        'maxlat',
        'minlon',
        'maxlon',
        'centlat',
        'centlon',
    )

admin.site.register(Geo, GeoAdmin)
