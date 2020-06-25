from django.test import TestCase
from django.urls import reverse

from . import factories


class AdminViewsTest(TestCase):
    def setUp(self):
        self.staff_user = factories.UserFactory(username="staff_user", is_staff=True)
        self.super_user = factories.UserFactory(
            username="super_user", is_staff=True, is_superuser=True
        )

    def test_delete_other_university(self):
        self.client.force_login(self.staff_user)

        other_uni = factories.UniversityFactory(name="Other")

        data = {"confirm": True}
        url = reverse("admin:higher_health_university_delete", args=(other_uni.pk,))

        res = self.client.post(url, data=data)
        self.assertTrue(res.status_code, 200)

    def test_delete_other_campus(self):
        self.client.force_login(self.staff_user)

        other_uni = factories.UniversityFactory(name="Other")
        other_camp = factories.CampusFactory(name="Other", university=other_uni)

        data = {"confirm": True}
        url = reverse("admin:higher_health_campus_delete", args=(other_camp.pk,))

        res = self.client.post(url, data=data)
        self.assertTrue(res.status_code, 200)

    def test_delete_other_campus_superuser(self):
        self.client.force_login(self.super_user)

        other_uni = factories.UniversityFactory(name="Other")
        other_camp = factories.CampusFactory(name="Other", university=other_uni)

        data = {"confirm": True}
        url = reverse("admin:higher_health_campus_delete", args=(other_camp.pk,))

        res = self.client.post(url, data=data)
        self.assertTrue(res.status_code, 204)

        data = {"confirm": True}
        url = reverse("admin:higher_health_university_delete", args=(other_uni.pk,))
        res = self.client.post(url, data=data)
        self.assertTrue(res.status_code, 204)
