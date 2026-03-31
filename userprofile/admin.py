from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    list_display = ['name','description']
    list_filter = ['name']
    search_fields = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ['user','user_role','status']
    list_filter = ['user']
    search_fields = ['user']