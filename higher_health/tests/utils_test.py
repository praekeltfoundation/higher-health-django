def get_data(symptoms=0, exposure=False, age="<18", pre_existing_condition="not_sure"):
    return {
        "age_range": age,
        "symptoms_fever": "yes" if symptoms >= 1 else "no",
        "symptoms_cough": "yes" if symptoms >= 2 else "no",
        "symptoms_sore_throat": "yes" if symptoms >= 3 else "no",
        "symptoms_difficulty_breathing": "no",
        "symptoms_muscles_hurt": "no",
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
        "history_obesity": False,
        "history_diabetes": False,
        "history_hypertension": False,
        "history_cardiovascular": False,
    }
