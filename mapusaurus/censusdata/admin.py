from django.contrib import admin
from models import Census2010Race, Census2010HispanicOrigin, Census2010Sex, Census2010Age, Census2010RaceStats, Census2010Households

#def unbound_callable(geoid):
#    return geo.geo.name

class Census2010RaceAdmin(admin.ModelAdmin):
    actions = None

class Census2010HispanicOriginAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(Census2010HispanicOriginAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# Register your models here.
admin.site.register(Census2010Race, Census2010RaceAdmin)
admin.site.register(Census2010HispanicOrigin, Census2010HispanicOriginAdmin)
admin.site.register(Census2010Sex)
admin.site.register(Census2010Age)
admin.site.register(Census2010RaceStats)
admin.site.register(Census2010Households)