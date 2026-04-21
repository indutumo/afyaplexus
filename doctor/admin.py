from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

@admin.register(Doctor)
class DoctorAdmin(ImportExportModelAdmin):
    list_display = ['status','name','mobile_number']
    list_filter = ['status','name']
    search_fields = ['status','name']