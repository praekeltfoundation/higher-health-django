from import_export import resources

from higher_health import models


class UniversityResource(resources.ModelResource):

    class Meta:
        model = models.University
        fields = ('id', 'name', 'province')


class CampusResource(resources.ModelResource):

    class Meta:
        model = models.Campus
        fields = ('id', 'name', 'university__name', 'university_id')

    def before_import(self, dataset, *args, **kwargs):
        if 'id' not in dataset.headers:
            dataset.insert_col('', lambda row: "", header='id')

        if 'university_id' not in dataset.headers:
            dataset.insert_col('', lambda row: "", header='university_id')

        uni = models.University.objects.all()

        for row in dataset.rows:
            row['university_id'] = uni.filter(name=row['name']).first().pk


