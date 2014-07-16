from django.contrib.gis import admin
from models import Geo

# Register your models here.
admin.site.register(Geo, admin.GeoModelAdmin)
