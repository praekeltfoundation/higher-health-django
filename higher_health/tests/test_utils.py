from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from higher_health.utils import get_risk_level, save_data

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


class SaveDataTestCase(TestCase):
    @mock.patch("higher_health.utils.submit_healthcheck_to_eventstore")
    def test_submits_data_to_eventstore(self, task):
        """
        Calls the task to asynchronously submit the data to the eventstore
        """
        data = get_data()
        data["risk_level"] = get_risk_level(data)
        user = User.objects.create_user("27820001001")
        healthcheck = save_data(data, user)
        task.delay.assert_called_once_with(str(healthcheck.id))


class TestTemplateTags(TestCase):
    def test_expiry_template_filter(self):
        from higher_health.templatetags.temp_tags import expires

        val = timezone.now()
        self.assertEqual(
            expires(val, 0),
            timezone.datetime(
                year=val.year,
                month=val.month,
                day=val.day,
                hour=23,
                minute=59,
                second=59,
                microsecond=999,
                tzinfo=val.tzinfo,
            ),
        )

        val = timezone.now()
        end_val = val + timezone.timedelta(days=1)
        self.assertEqual(
            expires(val, 1, midnight=False),
            timezone.datetime(
                year=end_val.year,
                month=end_val.month,
                day=end_val.day,
                hour=end_val.hour,
                minute=end_val.minute,
                second=end_val.second,
                microsecond=end_val.microsecond,
                tzinfo=end_val.tzinfo,
            ),
        )
