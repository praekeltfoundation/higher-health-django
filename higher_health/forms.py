from urllib.parse import urlencode

import phonenumbers
import pycountry
import requests
from django import forms
from django.conf import settings
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

from higher_health import models
from higher_health.validators import za_phone_number


class HealthCheckQuestionnaire(forms.Form):
    YES = "yes"
    NO = "no"
    NOT_SURE = "not_sure"
    YES_NO = ((YES, "Yes"), (NO, "No"))
    YES_NO_NOT_SURE = ((YES, "Yes"), (NO, "No"), (NOT_SURE, "Not Sure"))

    PROVINCE_CHOICES = sorted(
        (s.code, s.name) for s in pycountry.subdivisions.get(country_code="ZA")
    )

    msisdn = forms.CharField(
        label="Enter your mobile number",
        widget=TextInput(attrs={"placeholder": "Mobile number"}),
        required=True,
        validators=[za_phone_number],
    )
    first_name = forms.CharField(
        label="Enter your name",
        widget=TextInput(attrs={"placeholder": "Name"}),
        required=True,
    )
    last_name = forms.CharField(
        label="Enter your surname",
        widget=TextInput(attrs={"placeholder": "Surname"}),
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
        label="Please provide us with the gender you identify as",
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
        label="Please select a province", choices=[("", "--------")] + PROVINCE_CHOICES
    )
    facility_destination_university = forms.ModelChoiceField(
        label="Please select an institution",
        queryset=models.University.objects.all(),
        required=False,
    )
    facility_destination_campus = forms.ModelChoiceField(
        label="Please select a campus",
        queryset=models.Campus.objects.all(),
        required=False,
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
        label="Please confirm that the information you shared is accurate to the best of your knowledge. Once you click the SUBMIT button, you will be unable to complete another HealthCheck for the next 24hours. Please note that the National Department of Health may contact you if necessary based on your responses?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        invalid_address = False
        data = args[0] if args else kwargs.get("data", None)
        if data:
            data = data.copy()
            if data.get("address"):
                querystring = urlencode(
                    {
                        "key": settings.SERVER_PLACES_API_KEY,
                        "input": data["address"],
                        "language": "en",
                        "components": "country:za",
                    }
                )
                response = requests.get(
                    f"https://maps.googleapis.com/maps/api/place/autocomplete/json?{querystring}"
                )
                location = response.json()
                if location["predictions"]:
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
                    geometry = response.json()["result"]["geometry"]["location"]
                    data["latitude"] = geometry["lat"]
                    data["longitude"] = geometry["lng"]
                else:
                    invalid_address = True
            kwargs.update({"data": data})
        super(HealthCheckQuestionnaire, self).__init__(*args, **kwargs)

        if invalid_address:
            self.add_error(
                "address",
                "If you have typed your address incorrectly, please try again. If you are unable to provide your address, please TYPE the name of your Suburb, Township, Town or Village (or nearest)",
            )

        if data:
            if data.get("medical_confirm_accuracy") == "no":
                self.add_error(
                    "medical_confirm_accuracy",
                    "You need to confirm that this information is accurate",
                )

    def clean_msisdn(self):
        number = phonenumbers.parse(self.cleaned_data["msisdn"], "ZA")
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    def clean(self):
        cleaned_data = super(HealthCheckQuestionnaire, self).clean()

        errors = dict()
        required = "This field is required."

        going_to_campus = cleaned_data.get("facility_destination") == "campus"
        if going_to_campus:
            campus = cleaned_data.get("facility_destination_campus")
            province = cleaned_data.get("facility_destination_province")
            university = cleaned_data.get("facility_destination_university")

            if not university:
                errors.update({"facility_destination_university": required})

            if not campus:
                errors.update({"facility_destination_campus": required})

            if (province and university) and not province == university.province:
                errors.update(
                    {
                        "facility_destination_university": "Please select a university that is in {}.".format(
                            province
                        )
                    }
                )

            if (university and campus) and not campus.university == university:
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


class HealthCheckLogin(forms.Form):
    phone = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Phone number"}),
        required=True,
        max_length=100,
    )
    fullname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Last name"}),
        required=True,
        max_length=100,
    )
