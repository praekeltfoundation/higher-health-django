import base64
import hmac
import logging
from datetime import datetime, timedelta
from hashlib import sha256
from urllib.parse import urlencode

import phonenumbers
import pycountry
import requests
import secrets
import string
from django import forms
from django.conf import settings
from django.forms.widgets import NumberInput, TextInput
from django.utils.translation import ugettext_lazy as _
from temba_client.exceptions import TembaException

from higher_health import models
from higher_health.models import Covid19Triage
from higher_health.utils import iso6709_to_lat_lng, rapidpro
from higher_health.validators import za_phone_number

logger = logging.getLogger(__name__)


class HealthCheckQuestionnaire(forms.Form):
    YES = "yes"
    NO = "no"
    NOT_SURE = "not_sure"
    YES_NO = ((YES, "Yes"), (NO, "No"))
    YES_NO_NOT_SURE = ((YES, "Yes"), (NO, "No"), (NOT_SURE, "Not Sure"))

    PROVINCE_CHOICES = sorted(
        (s.code, s.name) for s in pycountry.subdivisions.get(country_code="ZA")
    )

    first_name = forms.CharField(
        label="Enter your name:",
        widget=TextInput(
            attrs={"placeholder": "Name", "aria-label": "Name input field"}
        ),
        required=True,
    )
    last_name = forms.CharField(
        label="Enter your surname:",
        widget=TextInput(
            attrs={"placeholder": "Surname", "aria-label": "Surname input field"}
        ),
        required=True,
    )
    age_range = forms.ChoiceField(
        label="How old are you?",
        choices=(
            ("", _("Age")),
            ("<18", _("<18")),
            ("18-39", _("18-39")),
            ("40-65", _("40-65")),
            (">65", _(">65")),
        ),
        required=True,
    )
    gender = forms.ChoiceField(
        label="Please provide us with the gender you identify as:",
        choices=(
            ("", _("Gender")),
            ("male", _("Male")),
            ("female", _("Female")),
            ("other", _("Other")),
            ("not_say", _("Rather not say")),
        ),
        required=True,
    )

    latitude = forms.CharField(widget=forms.HiddenInput())
    longitude = forms.CharField(widget=forms.HiddenInput())
    city = forms.CharField(required=False)
    address = forms.CharField(required=True)

    street_number = forms.CharField(required=False)
    route = forms.CharField(required=False)
    country = forms.CharField(required=False)

    DESTINATION_CHOICES = (("campus", "Campus (Student/Staff)"), ("office", "Office"))

    REASON_CHOICES = (
        ("student", "Student"),
        ("staff", "Staff"),
        ("visitor", "Visitor"),
    )

    facility_destination = forms.ChoiceField(
        label="", choices=DESTINATION_CHOICES, widget=forms.RadioSelect
    )
    facility_destination_province = forms.ChoiceField(
        label="Please select a province:", choices=[("", "--------")] + PROVINCE_CHOICES
    )
    facility_destination_university = forms.ModelChoiceField(
        label="Please select an institution:",
        queryset=models.University.objects.all(),
        required=False,
    )
    facility_destination_university_other = forms.CharField(
        label="If other, enter the name of the institution:", required=False
    )
    facility_destination_campus = forms.ModelChoiceField(
        label="Please select a campus:",
        queryset=models.Campus.objects.all(),
        required=False,
    )
    facility_destination_campus_other = forms.CharField(
        label="If other, enter the name of a campus:", required=False
    )
    facility_destination_reason = forms.ChoiceField(
        label="Are you a:", choices=REASON_CHOICES, widget=forms.RadioSelect
    )
    history_pre_existing_condition = forms.ChoiceField(
        label="Do you have any other pre-existing medical conditions that we should be aware of?",
        widget=forms.RadioSelect,
        choices=models.Covid19Triage.EXPOSURE_CHOICES,
        required=True,
    )
    history_obesity = forms.ChoiceField(
        label="Has a doctor or other health professional diagnosed you with Obesity?",
        widget=forms.RadioSelect,
        choices=models.Covid19Triage.YesNoBoolChoice._choices(),
        required=False,
    )
    history_diabetes = forms.ChoiceField(
        label="Has a doctor or other health professional diagnosed you with Diabetes?",
        widget=forms.RadioSelect,
        choices=models.Covid19Triage.YesNoBoolChoice._choices(),
        required=False,
    )
    history_hypertension = forms.ChoiceField(
        label="Has a doctor or other health professional diagnosed you with Hypertension?",
        widget=forms.RadioSelect,
        choices=models.Covid19Triage.YesNoBoolChoice._choices(),
        required=False,
    )
    history_cardiovascular = forms.ChoiceField(
        label="Has a doctor or other health professional diagnosed you with Cardiovascular Disease?",
        widget=forms.RadioSelect,
        choices=models.Covid19Triage.YesNoBoolChoice._choices(),
        required=False,
    )

    symptoms_fever = forms.ChoiceField(
        label="Do you feel very hot or cold? Are you sweating or shivering? When you touch your forehead, does it feel hot?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_cough = forms.ChoiceField(
        label="Do you have a cough that recently started?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_sore_throat = forms.ChoiceField(
        label="Do you have a sore throat or pain when swallowing that recently started?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_difficulty_breathing = forms.ChoiceField(
        label="Do you have breathlessness or difficulty in breathing, that you’ve noticed recently?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_taste = forms.ChoiceField(
        label="Have you noticed any recent changes in your ability to taste or smell things?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    medical_exposure = forms.ChoiceField(
        label="Have you recently been in close contact to someone confirmed to be infected with COVID-19?",
        choices=YES_NO_NOT_SURE,
        widget=forms.RadioSelect,
        required=True,
    )
    medical_confirm_accuracy = forms.ChoiceField(
        label="Please confirm that the information you shared is accurate to the best of your knowledge. Once you click the SUBMIT button, you will be unable to complete another HealthCheck for the next 24hours. Please note that the National Department of Health may contact you if necessary based on your responses.",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )

    def get_coords(self, user, address):
        """
        Returns a tuple of:

        invalid_address
        lookup_error
        latitude
        longitude
        """
        # First try to get existing coords if address matches
        try:
            # TODO: This could be optimised to check across all users, but then we would
            # need an index, so we first need to see how prevalent shared addresses are
            # between users before implementing
            existing = Covid19Triage.objects.filter(user=user, address=address).latest(
                "timestamp"
            )
            lat, lng = iso6709_to_lat_lng(existing.location)
            if lat and lng:
                return False, False, lat, lng
        except Covid19Triage.DoesNotExist:
            pass

        # Otherwise do google places lookup
        try:
            querystring = urlencode(
                {
                    "key": settings.SERVER_PLACES_API_KEY,
                    "input": address,
                    "language": "en",
                    "components": "country:za",
                }
            )
            response = requests.get(
                f"https://maps.googleapis.com/maps/api/place/autocomplete/json?{querystring}"
            )
            location = response.json()
            if not location["predictions"]:
                return True, False, None, None
            querystring = urlencode(
                {
                    "key": settings.SERVER_PLACES_API_KEY,
                    "place_id": location["predictions"][0]["place_id"],
                    "language": "en",
                    "fields": "geometry",
                }
            )
            response = requests.get(
                f"https://maps.googleapis.com/maps/api/place/details/json?{querystring}"
            )
            place_details = response.json()
            geometry = place_details["result"]["geometry"]["location"]
            return False, False, geometry["lat"], geometry["lng"]
        except (KeyError, requests.RequestException):
            logger.exception("Google Places lookup error")
            return False, True, None, None

    def __init__(self, *args, **kwargs):
        data = args[0] if args else kwargs.get("data", None)
        user = kwargs.pop("user")
        invalid_address = False
        address_lookup_error = False

        if data:
            data = data.copy()
            if data.get("address"):
                invalid_address, address_lookup_error, lat, lng = self.get_coords(
                    user, data["address"]
                )
                if lat and lng:
                    data["latitude"] = lat
                    data["longitude"] = lng
            kwargs.update({"data": data})
        super(HealthCheckQuestionnaire, self).__init__(*args, **kwargs)

        if invalid_address:
            self.add_error(
                "address",
                "If you have typed your address incorrectly, please try again. If you are unable to provide your address, please TYPE the name of your Suburb, Township, Town or Village (or nearest)",
            )
        if address_lookup_error:
            self.add_error(
                "address",
                "Sorry, we had a temporary error trying to validate this address, please try again",
            )

        if data:
            if data.get("medical_confirm_accuracy") == "no":
                self.add_error(
                    "medical_confirm_accuracy",
                    "You need to confirm that this information is accurate.",
                )

    def clean(self):
        cleaned_data = super(HealthCheckQuestionnaire, self).clean()

        errors = dict()
        required = "This field is required."

        going_to_campus = cleaned_data.get("facility_destination") == "campus"
        if going_to_campus:
            campus = cleaned_data.get("facility_destination_campus")
            campus_other = cleaned_data.get("facility_destination_campus_other")
            province = cleaned_data.get("facility_destination_province")
            university = cleaned_data.get("facility_destination_university")
            university_other = cleaned_data.get("facility_destination_university_other")

            if not university and not university_other:
                errors.update({"facility_destination_university": required})

            if not campus and not campus_other:
                errors.update({"facility_destination_campus": required})

            if (
                university
                and university.name.lower() == "other"
                and not university_other
            ):
                errors.update({"facility_destination_university_other": required})

            if campus and campus.name.lower() == "other" and not campus_other:
                errors.update({"facility_destination_campus_other": required})

            if (province and university) and (
                not province == university.province and university.province
            ):
                errors.update(
                    {
                        "facility_destination_university": "Please select a university that is in {}.".format(
                            province
                        )
                    }
                )

            if (university and campus) and not campus.university_id == university.id:
                errors.update(
                    {
                        "facility_destination_campus": "Please select a campus that is in {}.".format(
                            university
                        )
                    }
                )

        has_pre_existing_conditions = cleaned_data.get(
            "history_pre_existing_condition"
        ) in ["yes", "not_sure"]

        if has_pre_existing_conditions:
            cardiovascular = cleaned_data.get("history_cardiovascular")
            obesity = cleaned_data.get("history_obesity")
            diabetes = cleaned_data.get("history_diabetes")
            hypertension = cleaned_data.get("history_hypertension")

            if not cardiovascular:
                errors.update({"history_cardiovascular": required})

            if not obesity:
                errors.update({"history_obesity": required})

            if not diabetes:
                errors.update({"history_diabetes": required})

            if not hypertension:
                errors.update({"history_hypertension": required})
        else:
            cleaned_data["history_cardiovascular"] = False
            cleaned_data["history_obesity"] = False
            cleaned_data["history_diabetes"] = False
            cleaned_data["history_hypertension"] = False

        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data

    def registration_fields(self):
        return [
            self["first_name"],
            self["last_name"],
            self["age_range"],
            self["gender"],
        ]

    def destination_fields(self):
        return [
            self["facility_destination"],
            self["facility_destination_province"],
            self["facility_destination_university"],
            self["facility_destination_university_other"],
            self["facility_destination_campus"],
            self["facility_destination_campus_other"],
            self["facility_destination_reason"],
        ]

    def history_fields(self):
        return [
            self["history_obesity"],
            self["history_diabetes"],
            self["history_hypertension"],
            self["history_cardiovascular"],
        ]

    def medical_fields(self):
        return [
            self["symptoms_fever"],
            self["symptoms_cough"],
            self["symptoms_sore_throat"],
            self["symptoms_difficulty_breathing"],
            self["symptoms_taste"],
            self["medical_exposure"],
            self["medical_confirm_accuracy"],
        ]

    def registration_fields_has_errors(self):
        return any(
            [
                field
                for field in self.registration_fields() + [self["address"]]
                if field.errors
            ]
        )

    def destination_fields_has_errors(self):
        return any([field for field in self.destination_fields() if field.errors])

    def history_fields_has_errors(self):
        return any([field for field in self.history_fields() if field.errors])

    def medical_fields_has_errors(self):
        return any([field for field in self.medical_fields() if field.errors])


class HealthCheckLogin(forms.Form):
    msisdn = forms.CharField(
        label="Enter your mobile number below:",
        widget=TextInput(
            attrs={
                "placeholder": "Mobile number",
                "aria-label": "Mobile number input field",
            }
        ),
        required=True,
        validators=[za_phone_number],
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean_msisdn(self):
        number = phonenumbers.parse(self.cleaned_data["msisdn"], "ZA")
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    def send_otp_sms(self, msisdn):
        if (
            "otp_retries" in self.request.session
            and self.request.session["otp_retries"] >= settings.OTP_RETRIES_LIMIT
        ):
            if (
                "otp_timestamp" in self.request.session
                and (
                    datetime.utcnow() - timedelta(seconds=settings.OTP_BACKOFF_DURATION)
                ).timestamp()
                < self.request.session["otp_timestamp"]
            ):
                self.add_error(
                    "msisdn",
                    "You've exceeded the number of times you can request an OTP. Please try again later.",
                )
                return
            else:
                self.request.session["otp_retries"] = 0

        if "otp_retries" in self.request.session:
            self.request.session["otp_retries"] += 1
        else:
            self.request.session["otp_retries"] = 1

        otp = "".join(secrets.choice(string.digits) for _ in range(6))
        h = hmac.new(settings.SECRET_KEY.encode(), otp.encode(), digestmod=sha256)
        otp_hash = base64.b64encode(h.digest()).decode()
        self.request.session["otp_hash"] = otp_hash
        self.request.session["otp_timestamp"] = datetime.utcnow().timestamp()

        if rapidpro:
            try:
                rapidpro.create_flow_start(
                    params={"otp": otp},
                    flow=settings.RAPIDPRO_SEND_OTP_SMS_FLOW,
                    urns=[f"tel:{msisdn}"],
                )
            except TembaException:
                self.add_error(
                    "msisdn",
                    "We're unable to send you an OTP at this time. Please try again.",
                )

    def clean(self):
        cleaned_data = super().clean()
        msisdn = cleaned_data.get("msisdn")
        if msisdn:
            self.send_otp_sms(msisdn)


class HealthCheckOTP(forms.Form):
    otp = forms.CharField(
        label="Enter 6 digit pin sent via SMS",
        widget=NumberInput(attrs={"placeholder": "One Time Pin"}),
        required=True,
        min_length=6,
        max_length=6,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def verify_otp(self, otp):
        try:
            session_otp = self.request.session["otp_hash"]
            session_otp_timestamp = self.request.session["otp_timestamp"]
            h = hmac.new(settings.SECRET_KEY.encode(), otp.encode(), digestmod=sha256)
            if hmac.compare_digest(base64.b64encode(h.digest()).decode(), session_otp):
                self.request.session.pop("otp_hash")
                self.request.session.pop("otp_timestamp")
                if datetime.fromtimestamp(session_otp_timestamp) < (
                    datetime.utcnow() - timedelta(seconds=settings.OTP_EXPIRES_DURATION)
                ):
                    self.add_error(
                        "otp",
                        "The OTP you have entered has expired. Please reset and try again.",
                    )
            else:
                self.add_error("otp", "The OTP you have entered is incorrect.")
        except KeyError:
            self.add_error("otp", "The OTP you have entered is incorrect.")

    def clean_otp(self):
        self.verify_otp(self.cleaned_data["otp"])
