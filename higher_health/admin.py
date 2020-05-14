from django.contrib import admin

from . import models


@admin.register(models.University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ["name", "province"]
    list_filter = ["province"]
    search_fields = ["name"]


@admin.register(models.Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ["name", "university"]
    list_filter = ["university"]
    search_fields = ["name"]
