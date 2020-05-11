from django.test import TestCase

from higher_health.utils import get_risk_level

from .utils_test import get_data


class RiskLevelTestCase(TestCase):
    def test_get_risk_level_3_or_more_symptoms(self):
        data = get_data(symptoms=3)
        self.assertEqual(get_risk_level(data), "high")

    def test_get_risk_level_2_symptoms_and_exposure(self):
        data = get_data(symptoms=2, exposure=True)
        self.assertEqual(get_risk_level(data), "high")

    def test_get_risk_level_2_symptoms_and_age_over_65(self):
        data = get_data(symptoms=2, age=">65")
        self.assertEqual(get_risk_level(data), "high")

    def test_get_risk_level_2_symptoms_only(self):
        data = get_data(symptoms=2)
        self.assertEqual(get_risk_level(data), "moderate")

    def test_get_risk_level_1_symptom_and_exposure(self):
        data = get_data(symptoms=1, exposure=True)
        self.assertEqual(get_risk_level(data), "high")

    def test_get_risk_level_1_symptom_only(self):
        data = get_data(symptoms=1)
        self.assertEqual(get_risk_level(data), "moderate")

    def test_get_risk_level_0_symptoms_and_exposure(self):
        data = get_data(symptoms=0, exposure=True)
        self.assertEqual(get_risk_level(data), "moderate")

    def test_get_risk_level_0_symptoms_only(self):
        data = get_data(symptoms=0)
        self.assertEqual(get_risk_level(data), "low")

    def test_get_pre_existing_condition_yes_and_no_symptoms(self):
        data = get_data(symptoms=0, pre_existing_condition="yes")
        self.assertEqual(get_risk_level(data), "low")
