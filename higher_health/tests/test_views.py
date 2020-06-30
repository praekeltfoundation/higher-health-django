import base64
import hmac
from datetime import datetime, timedelta
from hashlib import sha256

import mock
import responses
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from higher_health.models import Covid19Triage
from higher_health.utils import get_location, save_data

from . import factories
from .utils_test import get_data, login_with_otp


class QuestionnaireTest(TestCase):
    def test_otp_only_used_once_per_session(self):
        response = login_with_otp(self.client, "+27831231234")
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse("healthcheck_otp"), {"otp": "111111"})
        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(errors["otp"], ["The OTP you have entered is incorrect."])

    def test_otp_session_retries_limit_exceeded(self):
        # attempt to login 3 times
        for i in range(0, 3):
            response = self.client.post(
                reverse("healthcheck_login"), {"msisdn": "+27831231234"}
            )
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, "/otp/")

        response = self.client.post(
            reverse("healthcheck_login"), {"msisdn": "+27831231234"}
        )

        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(
            errors["msisdn"],
            [
                "You've exceeded the number of times you can request an OTP. Please try again later."
            ],
        )

        # wait the duration of the cool off period
        session = self.client.session
        session["otp_timestamp"] = (
            datetime.utcnow() - timedelta(seconds=settings.OTP_BACKOFF_DURATION + 60)
        ).timestamp()
        session.save()

        response = self.client.post(
            reverse("healthcheck_login"), {"msisdn": "+27831231234"}
        )
        self.assertEqual(response.status_code, 302)

        # attempt to login 2 more times
        for i in range(0, 2):
            response = self.client.post(
                reverse("healthcheck_login"), {"msisdn": "+27831231234"}
            )
            self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("healthcheck_login"), {"msisdn": "+27831231234"}
        )

        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(
            errors["msisdn"],
            [
                "You've exceeded the number of times you can request an OTP. Please try again later."
            ],
        )

    def test_otp_expires(self):
        self.client.post(reverse("healthcheck_login"), {"msisdn": "+27831231234"})
        h = hmac.new(settings.SECRET_KEY.encode(), "111222".encode(), digestmod=sha256)
        fake_otp_hash = base64.b64encode(h.digest()).decode()
        session = self.client.session
        session["otp_hash"] = fake_otp_hash
        session["otp_timestamp"] = (
            datetime.utcnow() - timedelta(seconds=settings.OTP_EXPIRES_DURATION + 60)
        ).timestamp()
        session.save()
        response = self.client.post(reverse("healthcheck_otp"), {"otp": "111222"})
        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(
            errors["otp"],
            ["The OTP you have entered has expired. Please reset and try again."],
        )

    def test_get_with_empty_session(self):
        response = self.client.get(reverse("healthcheck_questionnaire"))
        self.assertRedirects(response, "/login/?next=%2F")

        login_with_otp(self.client, "+27831231234")

        response = self.client.get(reverse("healthcheck_questionnaire"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_questionnaire.html"
        )
        self.assertIn("form", response.context)

    def test_get_with_existing_triage(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["risk_level"] = "high"
        save_data(data, User.objects.get(username="+27831231234"))

        response = self.client.get(reverse("healthcheck_questionnaire"))
        self.assertRedirects(response, "/receipt/")

        response = self.client.get("/?redo=true")

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
        self.assertEqual(initial_data["address"], data["address"])
        self.assertEqual(initial_data["city"], data["city"])
        self.assertEqual(initial_data["street_number"], data["street_number"])
        self.assertEqual(initial_data["route"], data["route"])
        self.assertEqual(initial_data["country"], data["country"])

        self.assertEqual(
            initial_data["facility_destination"], data["facility_destination"]
        )
        self.assertEqual(
            initial_data["facility_destination_province"],
            data["facility_destination_province"],
        )
        self.assertEqual(
            initial_data["facility_destination_reason"],
            data["facility_destination_reason"],
        )

        self.assertFalse(initial_data["history_obesity"])
        self.assertFalse(initial_data["history_diabetes"])
        self.assertFalse(initial_data["history_hypertension"])
        self.assertFalse(initial_data["history_cardiovascular"])

    def test_get_with_no_triage_completed(self):
        response = self.client.get(reverse("healthcheck_questionnaire"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/")

        login_with_otp(self.client, "+27831231234")

        response = self.client.get(reverse("healthcheck_questionnaire"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_questionnaire.html"
        )
        self.assertIn("form", response.context)

        self.assertEqual(response.context["form"].initial, {})

    def test_post_with_invalid_data(self):
        login_with_otp(self.client, "+27831231234")

        response = self.client.post(reverse("healthcheck_questionnaire"), {})

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].errors
        self.assertEqual(errors["first_name"], ["This field is required."])
        self.assertEqual(errors["last_name"], ["This field is required."])
        self.assertEqual(errors["age_range"], ["This field is required."])
        self.assertEqual(errors["gender"], ["This field is required."])
        self.assertEqual(errors["latitude"], ["This field is required."])
        self.assertEqual(errors["longitude"], ["This field is required."])
        self.assertEqual(errors["address"], ["This field is required."])
        self.assertEqual(errors["symptoms_fever"], ["This field is required."])
        self.assertEqual(errors["symptoms_cough"], ["This field is required."])
        self.assertEqual(errors["symptoms_sore_throat"], ["This field is required."])
        self.assertEqual(
            errors["symptoms_difficulty_breathing"], ["This field is required."]
        )
        self.assertEqual(errors["symptoms_taste"], ["This field is required."])
        self.assertEqual(errors["medical_exposure"], ["This field is required."])
        self.assertEqual(
            errors["history_pre_existing_condition"], ["This field is required."]
        )
        self.assertEqual(
            errors["medical_confirm_accuracy"], ["This field is required."]
        )

        self.assertTrue(response.context["form"].registration_fields_has_errors)
        self.assertTrue(response.context["form"].destination_fields_has_errors)
        self.assertTrue(response.context["form"].history_fields_has_errors)
        self.assertTrue(response.context["form"].medical_fields_has_errors)

    def test_post_with_invalid_accuracy(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["medical_confirm_accuracy"] = "no"
        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].errors
        self.assertEqual(
            errors["medical_confirm_accuracy"],
            ["You need to confirm that this information is accurate"],
        )

        self.assertTrue(response.context["form"].registration_fields_has_errors())
        self.assertFalse(response.context["form"].destination_fields_has_errors())
        self.assertFalse(response.context["form"].history_fields_has_errors())
        self.assertTrue(response.context["form"].medical_fields_has_errors())

    @responses.activate
    @mock.patch("higher_health.utils.submit_healthcheck_to_eventstore")
    def test_post_get_coordinates_from_address(self, _):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "4 friend street woodstock"

        places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?key=TEST_API_KEY&input=4+friend+street+woodstock&language=en&components=country%3Aza"

        responses.add(
            responses.GET,
            places_url,
            json={"predictions": [{"place_id": "resultplaceid"}]},
            status=200,
            match_querystring=True,
        )

        places_detail_url = "https://maps.googleapis.com/maps/api/place/details/json?key=TEST_API_KEY&place_id=resultplaceid&language=en&fields=geometry"
        responses.add(
            responses.GET,
            places_detail_url,
            json={"result": {"geometry": {"location": {"lat": 11.1, "lng": 22.2}}}},
            status=200,
            match_querystring=True,
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 302)

        places_call, places_detail_call = responses.calls
        self.assertEqual(places_call.request.method, "GET")
        self.assertEqual(places_call.request.url, places_url)

        self.assertEqual(places_detail_call.request.method, "GET")
        self.assertEqual(places_detail_call.request.url, places_detail_url)

        [triage] = Covid19Triage.objects.all()

        self.assertEqual(triage.age, "<18")
        self.assertFalse(triage.fever)
        self.assertFalse(triage.cough)
        self.assertFalse(triage.sore_throat)
        self.assertFalse(triage.difficulty_breathing)
        self.assertFalse(triage.smell)
        self.assertEqual(triage.exposure, "no")
        self.assertEqual(triage.preexisting_condition, "no")
        self.assertEqual(triage.msisdn, "+27831231234")
        self.assertEqual(triage.first_name, "Jane")
        self.assertEqual(triage.last_name, "Smith")
        self.assertEqual(triage.province, "ZA-WC")
        self.assertEqual(triage.city, "Cape Town")
        self.assertEqual(triage.gender, "female")
        self.assertEqual(triage.address, "4 friend street woodstock")
        self.assertEqual(
            triage.location, get_location({"latitude": "11.1", "longitude": "22.2"})
        )

    @responses.activate
    def test_post_going_to_campus(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["facility_destination"] = "campus"
        data["latitude"] = ""
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "4 friend street woodstock"

        places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?key=TEST_API_KEY&input=4+friend+street+woodstock&language=en&components=country%3Aza"

        responses.add(
            responses.GET,
            places_url,
            json={"predictions": [{"place_id": "resultplaceid"}]},
            status=200,
            match_querystring=True,
        )

        places_detail_url = "https://maps.googleapis.com/maps/api/place/details/json?key=TEST_API_KEY&place_id=resultplaceid&language=en&fields=geometry"
        responses.add(
            responses.GET,
            places_detail_url,
            json={"result": {"geometry": {"location": {"lat": 11.1, "lng": 22.2}}}},
            status=200,
            match_querystring=True,
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors,
            {
                "facility_destination_university": ["This field is required."],
                "facility_destination_campus": ["This field is required."],
            },
        )
        self.assertFalse(response.context["form"].registration_fields_has_errors())
        self.assertTrue(response.context["form"].destination_fields_has_errors())
        self.assertFalse(response.context["form"].history_fields_has_errors())
        self.assertFalse(response.context["form"].medical_fields_has_errors())

        university = factories.UniversityFactory(province="ZA-WC")
        campus = factories.CampusFactory(university=university)

        university_ec = factories.UniversityFactory(province="ZA-EC")
        campus_unknown = factories.CampusFactory(
            university=factories.UniversityFactory(province="ZA-WC")
        )
        data.update(
            {
                "facility_destination_university": university_ec.pk,
                "facility_destination_campus": campus_unknown.pk,
            }
        )
        response = self.client.post(reverse("healthcheck_questionnaire"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors,
            {
                "facility_destination_university": [
                    "Please select a university that is in ZA-WC."
                ],
                "facility_destination_campus": [
                    "Please select a campus that is in University (Eastern Cape)."
                ],
            },
        )

        data.update(
            {
                "facility_destination_university": university.pk,
                "facility_destination_campus": campus.pk,
            }
        )
        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 302)

        places_call, places_detail_call = responses.calls[:2]  # just check first
        self.assertEqual(places_call.request.method, "GET")
        self.assertEqual(places_call.request.url, places_url)

        self.assertEqual(places_detail_call.request.method, "GET")
        self.assertEqual(places_detail_call.request.url, places_detail_url)

        [triage] = Covid19Triage.objects.all()

        self.assertEqual(triage.age, "<18")
        self.assertFalse(triage.fever)
        self.assertFalse(triage.cough)
        self.assertFalse(triage.sore_throat)
        self.assertFalse(triage.difficulty_breathing)
        self.assertFalse(triage.smell)
        self.assertEqual(triage.exposure, "no")
        self.assertEqual(triage.preexisting_condition, "no")
        self.assertEqual(triage.msisdn, "+27831231234")
        self.assertEqual(triage.first_name, "Jane")
        self.assertEqual(triage.last_name, "Smith")
        self.assertEqual(triage.province, "ZA-WC")
        self.assertEqual(triage.city, "Cape Town")
        self.assertEqual(triage.gender, "female")
        self.assertEqual(triage.address, "4 friend street woodstock")
        self.assertEqual(
            triage.location, get_location({"latitude": "11.1", "longitude": "22.2"})
        )

    @responses.activate
    def test_post_drop_downs_other(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["facility_destination"] = "campus"
        data["latitude"] = ""
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "4 friend street woodstock"

        places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?key=TEST_API_KEY&input=4+friend+street+woodstock&language=en&components=country%3Aza"

        responses.add(
            responses.GET,
            places_url,
            json={"predictions": [{"place_id": "resultplaceid"}]},
            status=200,
            match_querystring=True,
        )

        places_detail_url = "https://maps.googleapis.com/maps/api/place/details/json?key=TEST_API_KEY&place_id=resultplaceid&language=en&fields=geometry"
        responses.add(
            responses.GET,
            places_detail_url,
            json={"result": {"geometry": {"location": {"lat": 11.1, "lng": 22.2}}}},
            status=200,
            match_querystring=True,
        )

        university_other = factories.UniversityFactory(name="other", province="")
        campus_other = factories.CampusFactory(
            name="other", university=university_other
        )

        data.update(
            {
                "facility_destination_university": university_other.pk,
                "facility_destination_campus": campus_other.pk,
            }
        )
        response = self.client.post(reverse("healthcheck_questionnaire"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors,
            {
                "facility_destination_university_other": ["This field is required."],
                "facility_destination_campus_other": ["This field is required."],
            },
        )

        data.update(
            {
                "facility_destination_university_other": "Unisa-abroad",
                "facility_destination_campus_other": "Unisa-atlantic-ocean",
            }
        )
        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 302)

        places_call = responses.calls[0]
        self.assertEqual(places_call.request.method, "GET")
        self.assertEqual(places_call.request.url, places_url)

        [triage] = Covid19Triage.objects.all()

        self.assertEqual(triage.facility_destination_university_other, "Unisa-abroad")
        self.assertEqual(
            triage.facility_destination_campus_other, "Unisa-atlantic-ocean"
        )

    @responses.activate
    def test_post_pre_existing_conditions(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["facility_destination"] = "office"
        data["latitude"] = ""
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "4 friend street woodstock"
        data["history_pre_existing_condition"] = "yes"
        data["history_cardiovascular"] = ""
        data["history_hypertension"] = ""
        data["history_diabetes"] = ""
        data["history_obesity"] = ""

        places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?key=TEST_API_KEY&input=4+friend+street+woodstock&language=en&components=country%3Aza"

        responses.add(
            responses.GET,
            places_url,
            json={"predictions": [{"place_id": "resultplaceid"}]},
            status=200,
            match_querystring=True,
        )

        places_detail_url = "https://maps.googleapis.com/maps/api/place/details/json?key=TEST_API_KEY&place_id=resultplaceid&language=en&fields=geometry"
        responses.add(
            responses.GET,
            places_detail_url,
            json={"result": {"geometry": {"location": {"lat": 11.1, "lng": 22.2}}}},
            status=200,
            match_querystring=True,
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors,
            {
                "history_cardiovascular": ["This field is required."],
                "history_hypertension": ["This field is required."],
                "history_diabetes": ["This field is required."],
                "history_obesity": ["This field is required."],
            },
        )

        self.assertFalse(response.context["form"].registration_fields_has_errors())
        self.assertFalse(response.context["form"].destination_fields_has_errors())
        self.assertTrue(response.context["form"].history_fields_has_errors())
        self.assertFalse(response.context["form"].medical_fields_has_errors())

        data.update(
            {
                "history_cardiovascular": "True",
                "history_hypertension": "True",
                "history_diabetes": "False",
                "history_obesity": "False",
            }
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)
        self.assertEqual(response.status_code, 302)

        places_call, places_detail_call = responses.calls[:2]  # just check first
        self.assertEqual(places_call.request.method, "GET")
        self.assertEqual(places_call.request.url, places_url)

        self.assertEqual(places_detail_call.request.method, "GET")
        self.assertEqual(places_detail_call.request.url, places_detail_url)

        [triage] = Covid19Triage.objects.all()

        self.assertEqual(triage.age, "<18")
        self.assertFalse(triage.fever)
        self.assertFalse(triage.cough)
        self.assertFalse(triage.sore_throat)
        self.assertFalse(triage.difficulty_breathing)
        self.assertFalse(triage.smell)
        self.assertEqual(triage.exposure, "no")
        self.assertEqual(triage.msisdn, "+27831231234")
        self.assertEqual(triage.first_name, "Jane")
        self.assertEqual(triage.last_name, "Smith")
        self.assertEqual(triage.province, "ZA-WC")
        self.assertEqual(triage.city, "Cape Town")
        self.assertEqual(triage.gender, "female")
        self.assertEqual(triage.address, "4 friend street woodstock")
        self.assertEqual(
            triage.location, get_location({"latitude": "11.1", "longitude": "22.2"})
        )
        self.assertEqual(triage.preexisting_condition, "yes")
        self.assertTrue(triage.history_cardiovascular)
        self.assertTrue(triage.history_hypertension)
        self.assertFalse(triage.history_diabetes)
        self.assertFalse(triage.history_obesity)

        data.update(
            {
                "history_pre_existing_condition": "no",
                "history_cardiovascular": "True",
                "history_hypertension": "True",
                "history_diabetes": "True",
                "history_obesity": "True",
            }
        )

        response = self.client.post(reverse("healthcheck_questionnaire"), data)
        self.assertEqual(response.status_code, 302)

        places_call = responses.calls[0]
        self.assertEqual(places_call.request.method, "GET")
        self.assertEqual(places_call.request.url, places_url)

        triage = Covid19Triage.objects.filter(msisdn="+27831231234").last()

        self.assertEqual(triage.preexisting_condition, "no")
        self.assertFalse(triage.history_cardiovascular)
        self.assertFalse(triage.history_hypertension)
        self.assertFalse(triage.history_diabetes)
        self.assertFalse(triage.history_obesity)

    @responses.activate
    def test_post_get_coordinates_from_invalid_address(self):
        data = get_data()
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "area 51"

        places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?key=TEST_API_KEY&input=area+51&language=en&components=country%3Aza"

        responses.add(
            responses.GET,
            places_url,
            json={"predictions": []},
            status=200,
            match_querystring=True,
        )

        login_with_otp(self.client, "+27831231234")
        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(
            errors["address"],
            [
                "If you have typed your address incorrectly, please try again. If you are unable to provide your address, please TYPE the name of your Suburb, Township, Town or Village (or nearest)"
            ],
        )

        self.assertTrue(response.context["form"].registration_fields_has_errors())
        self.assertFalse(response.context["form"].destination_fields_has_errors())
        self.assertFalse(response.context["form"].history_fields_has_errors())
        self.assertFalse(response.context["form"].medical_fields_has_errors())

    @responses.activate
    def test_post_google_places_lookup_error(self):
        data = get_data()
        data["latitude"] = ""
        data["longitude"] = ""
        data["address"] = "area 51"

        places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?key=TEST_API_KEY&input=area+51&language=en&components=country%3Aza"

        responses.add(
            responses.GET, places_url, json={}, status=200, match_querystring=True
        )

        login_with_otp(self.client, "+27831231234")
        response = self.client.post(reverse("healthcheck_questionnaire"), data)

        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        self.assertEqual(
            errors["address"],
            [
                "Sorry, we had a temporary error trying to validate this address, please try again"
            ],
        )

        self.assertTrue(response.context["form"].registration_fields_has_errors())
        self.assertFalse(response.context["form"].destination_fields_has_errors())
        self.assertFalse(response.context["form"].history_fields_has_errors())
        self.assertFalse(response.context["form"].medical_fields_has_errors())


class ReceiptTest(TestCase):
    def test_get_with_empty_session(self):
        response = self.client.get(reverse("healthcheck_receipt"))

        self.assertEqual(response.status_code, 302)

    def test_get_with_existing_triage_id(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["risk_level"] = "high"
        triage = save_data(data, User.objects.get(username="+27831231234"))

        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("healthcheck_receipt"))

        # allow a user to re-do a HealthCheck
        response = self.client.get("/?redo=true")
        self.assertEqual(response.status_code, 200)

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

        self.assertFalse(response.context["is_expired"])
        self.assertIn(
            "{} 23:59".format(triage.timestamp.strftime("%B %d, %Y,")),
            str(response.content),
        )

    def test_get_with_expired_receipt(self):
        login_with_otp(self.client, "+27831231234")

        data = get_data()
        data["risk_level"] = "high"
        triage = save_data(data, User.objects.get(username="+27831231234"))
        triage.timestamp = timezone.now() - timedelta(days=1)
        triage.save()

        response = self.client.get(reverse("healthcheck_receipt"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="healthcheck_receipt.html"
        )
        self.assertTrue(response.context["is_expired"])
        self.assertContains(response, "Your clearance certificate has expired.")

    def test_get_with_no_triage_completed(self):
        response = self.client.get(reverse("healthcheck_receipt"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/receipt/")

        login_with_otp(self.client, "+27831231234")

        response = self.client.get(reverse("healthcheck_receipt"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
