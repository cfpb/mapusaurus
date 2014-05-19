from django.contrib.gis import admin
from models import StateCensusTract

# Register your models here.
admin.site.register(StateCensusTract, admin.GeoModelAdmin)
