from django.test import TestCase
from django.core import management

from . import factories


class AdminViewsTest(TestCase):
    def test_create_dropdown_fields(self):
        uni1 = factories.UniversityFactory()
        camp1 = factories.CampusFactory(university=uni1)
        factories.CampusFactory(
            university=factories.UniversityFactory())

        management.call_command('create_other_dropdown_fields')

        self.assertEqual(
            uni1._meta.model.objects.all().count(),
            3)

        self.assertEqual(
            camp1._meta.model.objects.all().count(),
            3)

        self.assertEqual(
            uni1._meta.model.objects.filter(name__iexact='Other').first().sort_order,
            3)

        self.assertEqual(
            camp1._meta.model.objects.filter(name__iexact='Other').first().sort_order,
            3)

    def test_create_dropdown_fields_created(self):
        uni1 = factories.UniversityFactory()
        camp1 = factories.CampusFactory(university=uni1)
        factories.CampusFactory(
            name="Other",
            university=factories.UniversityFactory(name="Other"))

        management.call_command('create_other_dropdown_fields')

        self.assertEqual(
            uni1._meta.model.objects.all().count(),
            2)

        self.assertEqual(
            camp1._meta.model.objects.all().count(),
            2)

        self.assertEqual(
            uni1._meta.model.objects.filter(name__iexact='Other').first().sort_order,
            2)

        self.assertEqual(
            camp1._meta.model.objects.filter(name__iexact='Other').first().sort_order,
            2)
