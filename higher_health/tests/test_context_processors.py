from django.test import TestCase

from higher_health.context_processors import api_keys


class ApiKeysTestCase(TestCase):
    def test_api_keys(self):
        self.assertEqual(api_keys(None), {"PLACES_API_KEY": "TEST_API_KEY"})
