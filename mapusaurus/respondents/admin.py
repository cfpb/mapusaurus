from django.contrib import admin
from models import ZipcodeCityStateYear, Agency, ParentInstitution, Institution

admin.site.disable_action('delete_selected')
# Register your models here.

class ZipcodeCityStateYearAdmin(admin.ModelAdmin):
    readonly_fields = ('zip_code', 'plus_four', 'city', 'state', 'year')
    list_display = ['unique_name', 'zip_code', 'city', 'state', 'year']
    search_fields = ['zip_code']

class AgencyAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'full_name')
    readonly_fields = ('hmda_id', 'acronym', 'full_name')

class ParentInstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'rssd_id']
    search_fields = ['name']
    readonly_fields = (
        'year',
        'name',
        'city',
        'state',
        'country',
        'rssd_id'
    )

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'assets', 'mailing_address', 'zip_code', 'respondent_id', 'rssd_id']
    search_fields = ['name']
    #list_filter = ('agency__acronym')
    readonly_fields = (
        'year',
        'respondent_id',
        'agency',
        'assets',
        'tax_id',
        'name',
        'mailing_address',
        'zip_code',
        'assets',
        'rssd_id',
        'parent',
        'non_reporting_parent',
        'top_holder',
    )

admin.site.register(ZipcodeCityStateYear, ZipcodeCityStateYearAdmin)
admin.site.register(Agency, AgencyAdmin)
admin.site.register(ParentInstitution, ParentInstitutionAdmin)
admin.site.register(Institution, InstitutionAdmin)
