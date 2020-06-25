from typing import Text
from urllib.parse import urljoin

import requests
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from requests.exceptions import RequestException

from config.celery import app
from higher_health.models import Covid19Triage


@app.task(
    autoretry_for=(RequestException, SoftTimeLimitExceeded),
    retry_backoff=True,
    max_retries=15,
    acks_late=True,
    soft_time_limit=10,
    time_limit=15,
)
def submit_healthcheck_to_eventstore(healthcheck_id: Text) -> None:
    healthcheck = Covid19Triage.objects.select_related(
        "facility_destination_university",
        "facility_destination_campus",
        "facility_destination_campus__university",
    ).get(id=healthcheck_id)

    data = {
        "deduplication_id": str(healthcheck.id),
        "msisdn": healthcheck.msisdn,
        "first_name": healthcheck.first_name or "",
        "last_name": healthcheck.last_name or "",
        "source": healthcheck.source,
        "province": healthcheck.province,
        "city": healthcheck.city,
        "age": healthcheck.age,
        "date_of_birth": (
            healthcheck.date_of_birth.isoformat() if healthcheck.date_of_birth else None
        ),
        "fever": healthcheck.fever,
        "cough": healthcheck.cough,
        "sore_throat": healthcheck.sore_throat,
        "difficulty_breathing": healthcheck.difficulty_breathing,
        "exposure": healthcheck.exposure,
        # Our database field allows this to be `None`, but this is required on the API
        # so if we have `None`, we send `False`. We'll store the raw value in the
        # `data` field
        "tracing": bool(healthcheck.confirm_accuracy),
        "risk": healthcheck.risk,
        "gender": healthcheck.gender,
        "city_location": healthcheck.location,
        "smell": healthcheck.smell,
        "preexisting_condition": healthcheck.preexisting_condition,
        "rooms_in_household": healthcheck.rooms_in_household,
        "persons_in_household": healthcheck.persons_in_household,
        "completed_timestamp": healthcheck.completed_timestamp.isoformat(),
        "data": {
            "confirm_accuracy": healthcheck.confirm_accuracy,
            "address": healthcheck.address,
            "street_number": healthcheck.street_number,
            "route": healthcheck.route,
            "country": healthcheck.country,
            "destination": healthcheck.facility_destination,
            "university": (
                healthcheck.facility_destination_university.to_dict()
                if healthcheck.facility_destination_university
                else None
            ),
            "campus": (
                healthcheck.facility_destination_campus.to_dict()
                if healthcheck.facility_destination_campus
                else None
            ),
            "reason": healthcheck.facility_destination_reason,
            # TODO: Create a v4 of this API, with these four fields included, and then
            # switch to it
            "obesity": healthcheck.history_obesity,
            "diabetes": healthcheck.history_diabetes,
            "hypertension": healthcheck.history_hypertension,
            "cardiovascular": healthcheck.history_cardiovascular,
        },
    }

    response = requests.post(
        url=urljoin(settings.EVENTSTORE_URL, "/api/v3/covid19triage/"),
        headers={"Authorization": f"Token {settings.EVENTSTORE_TOKEN}"},
        json=data,
    )
    response.raise_for_status()
