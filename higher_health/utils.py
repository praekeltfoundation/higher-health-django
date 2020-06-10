from django.conf import settings
from temba_client.v2 import TembaClient

from higher_health.models import Covid19Triage

rapidpro = None
if settings.RAPIDPRO_URL and settings.RAPIDPRO_TOKEN:
    rapidpro = TembaClient(settings.RAPIDPRO_URL, settings.RAPIDPRO_TOKEN)


def get_risk_level(data):
    symptoms = 0
    for key, value in data.items():
        if "symptoms_" in key and value == "yes":
            symptoms += 1

    if symptoms >= 3:
        return "high"
    elif symptoms == 2:
        if data["medical_exposure"] == "yes" or data["age_range"] == ">65":
            return "high"
        else:
            return "moderate"
    elif symptoms == 1:
        if data["medical_exposure"] == "yes":
            return "high"
        else:
            return "moderate"
    elif symptoms == 0:
        if data["medical_exposure"] == "yes":
            return "moderate"
        else:
            return "low"

    return "not_sure"


def get_location(data):
    lat = data["latitude"]
    lng = data["longitude"]

    if "-" not in lat:
        lat = f"+{lat}"

    if "-" not in lng:
        lng = f"+{lng}"

    return f"{lat}{lng}/"


def save_data(data, user):

    return Covid19Triage.objects.create(
        **{
            "source": "WEB",
            "user": user,
            "msisdn": user.username,
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "province": data["facility_destination_province"],
            "city": data["city"],
            "age": data["age_range"],
            "fever": "yes" == data["symptoms_fever"],
            "cough": "yes" == data["symptoms_cough"],
            "sore_throat": "yes" == data["symptoms_sore_throat"],
            "difficulty_breathing": "yes" == data["symptoms_difficulty_breathing"],
            "exposure": data["medical_exposure"],
            "smell": "yes" == data["symptoms_taste"],
            "preexisting_condition": data["history_pre_existing_condition"],
            "risk": data["risk_level"],
            "location": get_location(data),
            "confirm_accuracy": "yes" == data["medical_confirm_accuracy"],
            "gender": data["gender"],
            "address": data["address"],
            "street_number": data["street_number"],
            "route": data["route"],
            "country": data["country"],
            "facility_destination": data.get("facility_destination"),
            "facility_destination_university": data.get(
                "facility_destination_university"
            ),
            "facility_destination_campus": data.get("facility_destination_campus"),
            "facility_destination_reason": data.get("facility_destination_reason"),
            "history_obesity": data.get("history_obesity") or False,
            "history_diabetes": data.get("history_diabetes") or False,
            "history_hypertension": data.get("history_hypertension") or False,
            "history_cardiovascular": data.get("history_cardiovascular") or False,
        }
    )
