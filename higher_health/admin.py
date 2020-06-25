from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from . import models, resources


class OtherPreventDeletionMixin:
    # prevent other model obj from being mistakenly deleted
    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.name.lower() == "other" and not request.user.is_superuser:
                return False
        return super(OtherPreventDeletionMixin, self).has_delete_permission(
            request, obj=None
        )


@admin.register(models.University)
class UniversityAdmin(
    OtherPreventDeletionMixin, ImportExportActionModelAdmin, admin.ModelAdmin
):
    resource_class = resources.UniversityResource
    list_display = ["name", "province"]
    list_filter = ["province"]
    search_fields = ["name"]


@admin.register(models.Campus)
class CampusAdmin(
    OtherPreventDeletionMixin, ImportExportActionModelAdmin, admin.ModelAdmin
):
    resource_class = resources.CampusResource
    list_display = ["name", "university"]
    list_filter = ["university"]
    search_fields = ["name"]
