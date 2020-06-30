from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand

from higher_health.models import Campus, University


class Command(BaseCommand):
    help = "Create Other dropdown fields"

    def handle(self, *args, **options):
        try:
            university, created = University.objects.get_or_create(
                name="Other", province=""
            )
        except MultipleObjectsReturned:
            university = University.objects.filter(name="Other", province="").first()
        university.sort_order = 1
        university.save()

        try:
            campus, created = Campus.objects.get_or_create(
                name="Other", university=university
            )
        except MultipleObjectsReturned:
            campus = Campus.objects.filter(name="Other", university=university).first()

        campus.sort_order = 1
        campus.save()
