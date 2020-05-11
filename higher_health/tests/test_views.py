import uuid

import responses
from django.test import TestCase
from django.urls import reverse

from higher_health.utils import save_data

from .utils_test import get_data


class QuestionnaireTest(TestCase):
    def test_get_with_empty_session(self):
        response = self.client.get(reverse("healthcheck_questionnaire"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_questionnaire.html"
        )
        self.assertIn("form", response.context)

    def test_get_with_triage_id_in_session(self):
        data = get_data()
        data["risk_level"] = "high"
        triage = save_data(data)

        session = self.client.session
        session["triage_id"] = str(triage.id)
        session.save()

        response = self.client.get(reverse("healthcheck_questionnaire"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_questionnaire.html"
        )
        self.assertIn("form", response.context)

        initial_data = response.context["form"].initial

        self.assertEqual(initial_data["msisdn"], data["msisdn"])
        self.assertEqual(initial_data["first_name"], data["first_name"])
        self.assertEqual(initial_data["last_name"], data["last_name"])
        self.assertEqual(initial_data["age_range"], data["age_range"])
        self.assertEqual(initial_data["gender"], data["gender"])
        self.assertEqual(initial_data["province"], data["province"])
        self.assertEqual(initial_data["address"], data["address"])
        self.assertEqual(initial_data["city"], data["city"])
        self.assertEqual(initial_data["street_number"], data["street_number"])
        self.assertEqual(initial_data["route"], data["route"])
        self.assertEqual(initial_data["country"], data["country"])

    def test_get_with_invalid_triage_id_in_session(self):
        session = self.client.session
        session["triage_id"] = str(uuid.uuid4())
        session.save()

        response = self.client.get(reverse("healthcheck_questionnaire"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_questionnaire.html"
        )
        self.assertIn("form", response.context)

        self.assertEqual(response.context["form"].initial, {})

    def test_post_with_invalid_data(self):
        response = self.client.post(reverse("healthcheck_questionnaire"), {})

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].errors
        self.assertEqual(errors["msisdn"], ["This field is required."])
        self.assertEqual(errors["first_name"], ["This field is required."])
        self.assertEqual(errors["last_name"], ["This field is required."])
        self.assertEqual(errors["age_range"], ["This field is required."])
        self.assertEqual(errors["gender"], ["This field is required."])
        self.assertEqual(errors["province"], ["This field is required."])
        self.assertEqual(errors["latitude"], ["This field is required."])
        self.assertEqual(errors["longitude"], ["This field is required."])
        self.assertEqual(errors["address"], ["This field is required."])
        self.assertEqual(errors["symptoms_fever"], ["This field is required."])
        self.assertEqual(errors["symptoms_cough"], ["This field is required."])
        self.assertEqual(errors["symptoms_sore_throat"], ["This field is required."])
        self.assertEqual(
            errors["symptoms_difficulty_breathing"], ["This field is required."]
        )
        self.assertEqual(errors["symptoms_muscles_hurt"], ["This field is required."])
        self.assertEqual(errors["symptoms_taste"], ["This field is required."])
        self.assertEqual(errors["medical_exposure"], ["This field is required."])
        self.assertEqual(
            errors["medical_pre_existing_condition"], ["This field is required."]
        )
        self.assertEqual(
            errors["medical_confirm_accuracy"], ["This field is required."]
        )

    def test_post_with_invalid_accuracy(self):
        data = get_data()
        data["medical_confirm_accuracy"] = "no"
        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].errors
        self.assertEqual(
            errors["medical_confirm_accuracy"],
            ["You need to confirm that this information is accurate"],
        )

    @responses.activate
    def test_post_get_coordinates_from_address(self):
        data = get_data()
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "4 friend street woodstock"

        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=TEST_API_KEY&input=4+friend+street+woodstock&inputtype=textquery&language=en&fields=geometry",
            json={
                "candidates": [
                    {"geometry": {"location": {"lat": "11.1", "lng": "22.2"}}}
                ]
            },
            status=200,
            match_querystring=True,
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 302)

    @responses.activate
    def test_post_get_coordinates_from_invalid_address(self):
        data = get_data()
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "area 51"

        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=TEST_API_KEY&input=area+51&inputtype=textquery&language=en&fields=geometry",
            json={"candidates": []},
            status=200,
            match_querystring=True,
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(errors["address"], ["Invalid address"])


class ReceiptTest(TestCase):
    def test_get_with_empty_session(self):
        response = self.client.get(reverse("healthcheck_receipt"))

        self.assertEqual(response.status_code, 302)

    def test_get_with_triage_id_in_session(self):
        data = get_data()
        data["risk_level"] = "high"
        triage = save_data(data)

        session = self.client.session
        session["triage_id"] = str(triage.id)
        session.save()

        response = self.client.get(reverse("healthcheck_receipt"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_receipt.html"
        )
        self.assertEqual(response.context["risk_level"], triage.risk)
        self.assertEqual(response.context["first_name"], triage.first_name)
        self.assertEqual(response.context["last_name"], triage.last_name)
        self.assertEqual(response.context["timestamp"], triage.timestamp)
        self.assertEqual(response.context["msisdn"], triage.hashed_msisdn)

    def test_get_with_invalid_triage_id_in_session(self):
        session = self.client.session
        session["triage_id"] = str(uuid.uuid4())
        session.save()

        response = self.client.get(reverse("healthcheck_receipt"))

        self.assertEqual(response.status_code, 302)
