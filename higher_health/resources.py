from import_export import resources

from higher_health import models


class UniversityResource(resources.ModelResource):

    class Meta:
        model = models.University
        fields = ('id', 'name', 'province')


class CampusResource(resources.ModelResource):

    class Meta:
        model = models.Campus
        fields = ('id', 'name', 'university__name')

