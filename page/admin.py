from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


@admin.register(Page)
class PageAdmin(ImportExportModelAdmin):
    list_display = ['page_type','title']
    list_filter = ['page_type']
    search_fields = ['page_type']

@admin.register(PageComment)
class PageCommentAdmin(ImportExportModelAdmin):
    list_display = ['page','comment']
    list_filter = ['page']
    search_fields = ['page']


@admin.register(PageAttachment)
class PageAttachmentAdmin(ImportExportModelAdmin):
    list_display = ['page','date']
    list_filter = ['page']
    search_fields = ['page']