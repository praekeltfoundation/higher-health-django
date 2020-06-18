from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from higher_health import models


class UniversityResource(resources.ModelResource):
    class Meta:
        model = models.University
        fields = ("id", "name", "province")


class UniversityForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row):
        return self.model.objects.filter(
            name__iexact=row["university"], province__iexact=row["university_province"]
        )


class CampusResource(resources.ModelResource):
    university = fields.Field(
        column_name="university",
        attribute="university",
        widget=UniversityForeignKeyWidget(models.University, "name"),
    )

    class Meta:
        model = models.Campus
        import_id_fields = ("name", "university")
        skip_unchanged = True
        fields = ("id", "name", "university", "university_province")
