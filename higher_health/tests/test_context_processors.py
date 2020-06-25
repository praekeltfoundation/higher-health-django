from django.test import TestCase, override_settings

from higher_health.context_processors import api_keys, ga_tags


class ApiKeysTestCase(TestCase):
    def test_api_keys(self):
        self.assertEqual(api_keys(None), {"PLACES_API_KEY": "TEST_API_KEY"})

    def test_multiple_api_keys(self):
        self.assertEqual(api_keys(None), {"PLACES_API_KEY": "TEST_API_KEY"})


class GATagKeysTestCase(TestCase):
    def test_ga_tag_keys(self):
        self.assertEqual(ga_tags(None), {"GA_TAGS": []})

        response = self.client.get("/login/")
        self.assertNotContains(response, "https://www.googletagmanager.com/")

    @override_settings(GA_TAG_KEYS=["test_key_1", "test_key_2"])
    def test_multiple_api_keys(self):
        self.assertEqual(ga_tags(None), {"GA_TAGS": ["test_key_1", "test_key_2"]})

        response = self.client.get("/login/")
        self.assertContains(
            response, "https://www.googletagmanager.com/gtag/js?id=test_key_1"
        )
        self.assertContains(
            response, "https://www.googletagmanager.com/gtag/js?id=test_key_2"
        )
