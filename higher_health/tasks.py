import logging
from typing import Text
from urllib.parse import urljoin

import requests
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from requests.exceptions import RequestException

from config.celery import app
from higher_health.models import Covid19Triage

logger = logging.getLogger(__name__)


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
        # city is a required field on the API, but address is allowed to be blank.
        # So we make sure that it is not blank. We'll store the original value in
        # data in case we need it.
        # We use the address, not city value here, because city is just the result
        # from the google places API, where as address is the formatted address, which
        # is what we actually want for city
        "city": healthcheck.address or "<None>",
        "age": {"18-39": "18-40"}.get(healthcheck.age, healthcheck.age),
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
            "city": healthcheck.city,
            "street_number": healthcheck.street_number,
            "route": healthcheck.route,
            "country": healthcheck.country,
            "destination": healthcheck.facility_destination,
            "university": (
                healthcheck.facility_destination_university.to_dict()
                if healthcheck.facility_destination_university
                else None
            ),
            "university_other": (
                healthcheck.facility_destination_university_other
                if healthcheck.facility_destination_university_other
                else None
            ),
            "campus": (
                healthcheck.facility_destination_campus.to_dict()
                if healthcheck.facility_destination_campus
                else None
            ),
            "campus_other": (
                healthcheck.facility_destination_campus_other
                if healthcheck.facility_destination_campus_other
                else None
            ),
            "reason": healthcheck.facility_destination_reason,
            # TODO: Create a v4 of this API, with these four fields included, and then
            # switch to it
            "obesity": healthcheck.history_obesity,
            "diabetes": healthcheck.history_diabetes,
            "hypertension": healthcheck.history_hypertension,
            "cardiovascular": healthcheck.history_cardiovascular,
            "vaccine_uptake": healthcheck.vaccine_uptake,
        },
    }
    if not settings.EVENTSTORE_URL or not settings.EVENTSTORE_TOKEN:
        logger.error(
            f"EVENTSTORE_URL and EVENTSTORE_TOKEN are not configured, not submitting {data} to eventstore"
        )
        return
    response = requests.post(
        url=urljoin(settings.EVENTSTORE_URL, "/api/v3/covid19triage/"),
        headers={"Authorization": f"Token {settings.EVENTSTORE_TOKEN}"},
        json=data,
    )
    response.raise_for_status()
