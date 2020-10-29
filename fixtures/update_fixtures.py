import csv
import sys

CAMPUS_FILENAME = "higherhealth_campuses.csv"
UNIVERSITY_FILENAME = "higherhealth_university_province.csv"


PROVINCE_MAPPING = {
    "EC": "ZA-EC",
    "Eastern Cape": "ZA-EC",
    "FS": "ZA-FS",
    "Free State": "ZA-FS",
    "GP": "ZA-GT",
    "Gauteng": "ZA-GT",
    "KZN": "ZA-NL",
    "KwaZulu-Natal": "ZA-NL",
    "LP": "ZA-LP",
    "Limpopo": "ZA-LP",
    "MP": "ZA-MP",
    "Mpumalanga": "ZA-MP",
    "NW": "ZA-NW",
    "North West": "ZA-NW",
    "NC": "ZA-NC",
    "Northern Cape": "ZA-NC",
    "WC": "ZA-WC",
    "Western Cape": "ZA-WC",
}


def get_csv(filename):
    with open(filename) as f:
        return list(csv.DictReader(f))


def append_csv(filename, data):
    with open(filename, "a") as f:
        writer = csv.writer(f)
        writer.writerows(data)


def update_campus(existing_data, new_data):
    existing_set = set(
        (d["university_province"].strip(), d["university"].strip(), d["name"].strip())
        for d in existing_data
    )

    def get_row(d):
        d = {k.strip().lower(): v.strip() for k, v in d.items()}
        province = PROVINCE_MAPPING[d["province"]]
        university = d.get("university") or d.get("tvet") or d["phei"]
        campus = d["campus"]
        return (province, university, campus)

    new_set = set(map(get_row, new_data))

    return new_set - existing_set


def update_university(existing_data, new_data):
    existing_set = set(
        (d["province"].strip(), d["name"].strip()) for d in existing_data
    )

    def get_row(d):
        d = {k.strip().lower(): v.strip() for k, v in d.items()}
        province = PROVINCE_MAPPING[d["province"]]
        university = d.get("university") or d.get("tvet") or d["phei"]
        return (province, university)

    new_set = set(map(get_row, new_data))

    return new_set - existing_set


if __name__ == "__main__":
    new_data = []
    for filename in sys.argv[1:]:
        new_data.extend(get_csv(filename))

    campus_data = get_csv(CAMPUS_FILENAME)
    campus_data_update = sorted(update_campus(campus_data, new_data))
    append_csv(CAMPUS_FILENAME, campus_data_update)

    university_data = get_csv(UNIVERSITY_FILENAME)
    university_data_update = sorted(update_university(university_data, new_data))
    university_data_update = [
        d + (i + len(university_data) + 1,)
        for i, d in enumerate(university_data_update)
    ]
    append_csv(UNIVERSITY_FILENAME, university_data_update)
