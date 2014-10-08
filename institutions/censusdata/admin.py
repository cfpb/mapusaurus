from django.contrib import admin
from models import Census2010Race, Census2010HispanicOrigin, Census2010Sex, Census2010Age, Census2010RaceStats, Census2010Households


# Register your models here.
admin.site.register(Census2010Race)
admin.site.register(Census2010HispanicOrigin)
admin.site.register(Census2010Sex)
admin.site.register(Census2010Age)
admin.site.register(Census2010RaceStats)
admin.site.register(Census2010Households)