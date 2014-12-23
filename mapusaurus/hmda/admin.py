from django.contrib.gis import admin
from models import HMDARecord, LendingStats
from geo.models import Geo

# Register your models here.


class GeoInline(admin.TabularInline):
    model = Geo

class HMDARecordAdmin(admin.ModelAdmin):
    list_display = ('institution', 'as_of_year', 'action_taken', 'statefp', 'countyfp')
    #inlines = [
    #    GeoInline,
    #]

class LendingStatsAdmin(admin.ModelAdmin):
    list_display = ('institution', 'lar_median')


admin.site.register(HMDARecord, HMDARecordAdmin)
admin.site.register(LendingStats, LendingStatsAdmin)
