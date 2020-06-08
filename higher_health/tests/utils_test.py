import base64
import hmac
from hashlib import sha256

from django.urls import reverse


def get_data(symptoms=0, exposure=False, age="<18", pre_existing_condition="no"):
    return {
        "age_range": age,
        "symptoms_fever": "yes" if symptoms >= 1 else "no",
        "symptoms_cough": "yes" if symptoms >= 2 else "no",
        "symptoms_sore_throat": "yes" if symptoms >= 3 else "no",
        "symptoms_difficulty_breathing": "no",
        "symptoms_taste": "no",
        "medical_exposure": "yes" if exposure else "no",
        "medical_confirm_accuracy": "yes",
        "latitude": "53.3913081",
        "longitude": "-2.109429099999999",
        "msisdn": "+27831231234",
        "first_name": "Jane",
        "last_name": "Smith",
        "city": "Cape Town",
        "gender": "female",
        "address": "",
        "street_number": "",
        "route": "",
        "country": "",
        "facility_destination": "office",
        "facility_destination_province": "ZA-WC",
        "facility_destination_reason": "staff",
        "history_pre_existing_condition": pre_existing_condition,
        "history_obesity": "",
        "history_diabetes": "",
        "history_hypertension": "",
        "history_cardiovascular": "",
    }


def login_with_otp(client, msisdn, otp="111111"):
    client.post(reverse("healthcheck_login"), {"msisdn": "+27831231234"})
    h = hmac.new(otp.encode(), digestmod=sha256)
    fake_otp_hash = base64.b64encode(h.digest()).decode()
    session = client.session
    session["otp_hash"] = fake_otp_hash
    session.save()
    client.post(reverse("healthcheck_otp"), {"otp": otp})
