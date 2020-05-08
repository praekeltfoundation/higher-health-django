from higher_health.models import Covid19Triage


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


def save_data(data, risk_level):
    return Covid19Triage.objects.create(
        **{
            "source": "WEB",
            "province": data["province"],
            "city": data["city"],
            "age": data["age_range"],
            "fever": "yes" == data["symptoms_fever"],
            "cough": "yes" == data["symptoms_cough"],
            "sore_throat": "yes" == data["symptoms_sore_throat"],
            "difficulty_breathing": "yes" == data["symptoms_difficulty_breathing"],
            "exposure": data["medical_exposure"],
            "muscle_pain": "yes" == data["symptoms_muscles_hurt"],
            "smell": "yes" == data["symptoms_taste"],
            "preexisting_condition": data["symptoms_pre_existing_condition"],
            "risk": risk_level,
            "location": get_location(data),
            "confirm_accuracy": "yes" == data["medical_confirm_accuracy"],
        }
    )
