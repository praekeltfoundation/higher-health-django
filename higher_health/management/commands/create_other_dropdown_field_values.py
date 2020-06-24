from django.core.management.base import BaseCommand
from higher_health.models import University, Campus


class Command(BaseCommand):
    help = "Create Other dropdown fields"

    def handle(self, *args, **options):
        university_count = University.objects.exclude(name="Other").count()
        university, created = University.objects.get_or_create(name="Other")

        university.sort_order = university_count + 1
        university.save()

        campus_count = Campus.objects.exclude(name="Other").count()
        campus, created = Campus.objects.get_or_create(
            name="Other", university=university
        )

        campus.sort_order = campus_count + 1
        campus.save()
