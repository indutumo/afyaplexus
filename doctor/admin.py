from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

@admin.register(Doctor)
class DoctorAdmin(ImportExportModelAdmin):
    list_display = ['status','name','mobile_number']
    list_filter = ['status','name']
    search_fields = ['status','name']


@admin.register(Partner)
class PartnerAdmin(ImportExportModelAdmin):
    list_display = ['status','name','mobile_number']
    list_filter = ['status','name']
    search_fields = ['status','name']


@admin.register(PatientSupport)
class PatientSupportAdmin(ImportExportModelAdmin):
    list_display = ['status','name','mobile_number']
    list_filter = ['status','name']
    search_fields = ['status','name']

@admin.register(Volunteer)
class VolunteerAdmin(ImportExportModelAdmin):
    list_display = ['status','name','mobile_number']
    list_filter = ['status','name']
    search_fields = ['status','name']