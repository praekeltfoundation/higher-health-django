from django.test import TestCase

from higher_health.utils import get_risk_level


def get_data(symptoms=0, exposure=False, age="<18", pre_existing_condition="not_sure"):
    return {
        "age_range": age,
        "symptoms_sweating": "yes" if symptoms >= 1 else "no",
        "symptoms_cough": "yes" if symptoms >= 2 else "no",
        "symptoms_sore_throat": "yes" if symptoms >= 3 else "no",
        "symptoms_difficulty_breathing": "no",
        "symptoms_muscles_hurt": "no",
        "symptoms_taste": "no",
        "medical_exposure": "yes" if exposure else "no",
        "medical_pre_existing_condition": pre_existing_condition,
        "medical_confirm_accuracy": "yes",
        "latitude": "53.3913081",
        "longitude": "-2.109429099999999",
    }


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
