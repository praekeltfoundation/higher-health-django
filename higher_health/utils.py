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
