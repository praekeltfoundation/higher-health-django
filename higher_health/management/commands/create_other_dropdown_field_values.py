from django.core.management.base import BaseCommand

from higher_health.models import Campus, University


class Command(BaseCommand):
    help = "Create Other dropdown fields"

    def handle(self, *args, **options):
        university, created = University.objects.get_or_create(name="Other")
        university.sort_order = 1
        university.save()

        campus, created = Campus.objects.get_or_create(
            name="Other", university=university
        )
        campus.sort_order = 1
        campus.save()
