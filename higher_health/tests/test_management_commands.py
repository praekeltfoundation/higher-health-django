from django.core import management
from django.test import TestCase

from . import factories


class AdminViewsTest(TestCase):
    def test_create_dropdown_fields(self):
        uni1 = factories.UniversityFactory()
        camp1 = factories.CampusFactory(university=uni1)
        factories.CampusFactory(university=factories.UniversityFactory())

        management.call_command("create_other_dropdown_field_values")

        self.assertEqual(uni1._meta.model.objects.all().count(), 3)

        self.assertEqual(camp1._meta.model.objects.all().count(), 3)

        self.assertEqual(
            uni1._meta.model.objects.filter(name__iexact="Other").first().sort_order, 1
        )

        self.assertEqual(
            camp1._meta.model.objects.filter(name__iexact="Other").first().sort_order, 1
        )

    def test_create_dropdown_fields_created(self):
        uni1 = factories.UniversityFactory()
        camp1 = factories.CampusFactory(university=uni1)
        factories.CampusFactory(
            name="Other", university=factories.UniversityFactory(
                name="Other", province='')
        )

        management.call_command("create_other_dropdown_field_values")

        self.assertEqual(
            uni1._meta.model.objects.filter(name__iexact="Other").first().sort_order, 1
        )

        self.assertEqual(
            camp1._meta.model.objects.filter(name__iexact="Other").first().sort_order, 1
        )
