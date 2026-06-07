from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


@admin.register(County)
class CountyAdmin(ImportExportModelAdmin):
    list_display = ['name']

@admin.register(Constituent)
class ConstituentAdmin(ImportExportModelAdmin):
    list_display = ['county','name']
    list_filter = ['county']
    search_fields = ['county']


@admin.register(Ward)
class WardAdmin(ImportExportModelAdmin):
    list_display = ['county','constituent','name']
    list_filter = ['county','constituent']
    search_fields = ['county','constituent']

@admin.register(Hospital)
class HospitalAdmin(ImportExportModelAdmin):
    list_display = ['county','name','mobile_number','google_pin']
    list_filter = ['county','name']
    search_fields = ['county','name']


@admin.register(DailysisService)
class DailysisServiceAdmin(ImportExportModelAdmin):
    list_display = ['hospital','name','description']
    list_filter = ['hospital','name']
    search_fields = ['hospital','name']

@admin.register(HospitalImage)
class HospitalImageAdmin(ImportExportModelAdmin):
    list_display = ['hospital','cover','status']
    list_filter = ['hospital']
    search_fields = ['hospital']


@admin.register(HospitalRating)
class HospitalRatingAdmin(ImportExportModelAdmin):
    list_display = ['hospital','rating','comment']
    list_filter = ['hospital']
    search_fields = ['hospital']

@admin.register(Appointment)
class AppointmentAdmin(ImportExportModelAdmin):
    list_display = ['hospital','name','appointment_date','mobile_number']
    list_filter = ['hospital']
    search_fields = ['hospital']

@admin.register(OperationDay)
class OperationDayAdmin(ImportExportModelAdmin):
    list_display = ['hospital','day','time_from','time_to']
    list_filter = ['hospital']
    search_fields = ['hospital']


@admin.register(PublicHoliday)
class PublicHolidayAdmin(ImportExportModelAdmin):
    list_display = ['name','date','status']
    list_filter = ['name']
    search_fields = ['name']