from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from . import models, resources


@admin.register(models.University)
class UniversityAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_class = resources.UniversityResource
    list_display = ["name", "province"]
    list_filter = ["province"]
    search_fields = ["name"]


@admin.register(models.Campus)
class CampusAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_class = resources.CampusResource
    list_display = ["name", "university"]
    list_filter = ["university"]
    search_fields = ["name"]
