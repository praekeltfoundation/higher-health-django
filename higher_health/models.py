import enum
import uuid

import pycountry
from django.db import models
from django.utils import timezone


class Choice(enum.Enum):
    @classmethod
    def _choices(cls):
        return [(i.value, i.name) for i in cls]


class University(models.Model):
    PROVINCE_CHOICES = sorted(
        (s.code, s.name) for s in pycountry.subdivisions.get(country_code="ZA")
    )
    name = models.CharField(max_length=100)
    province = models.CharField(choices=PROVINCE_CHOICES, max_length=100)

    def __str__(self):
        if not self.province:
            return "{0}".format(self.name)
        return "{0} ({1})".format(self.name, self.get_province_display())


class Campus(models.Model):
    name = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        if self.university.name.lower() == "other":
            return "{0}".format(self.name)
        return "{0} ({1})".format(self.name, self.university.name)


class Covid19Triage(models.Model):
    AGE_U18 = "<18"
    AGE_18T40 = "18-40"
    AGE_40T65 = "40-65"
    AGE_O65 = ">65"
    AGE_CHOICES = (
        (AGE_U18, AGE_U18),
        (AGE_18T40, AGE_18T40),
        (AGE_40T65, AGE_40T65),
        (AGE_O65, AGE_O65),
    )

    PROVINCE_CHOICES = sorted(
        (s.code, s.name) for s in pycountry.subdivisions.get(country_code="ZA")
    )

    EXPOSURE_YES = "yes"
    EXPOSURE_NO = "no"
    EXPOSURE_NOT_SURE = "not_sure"
    EXPOSURE_CHOICES = (
        (EXPOSURE_YES, "Yes"),
        (EXPOSURE_NO, "No"),
        (EXPOSURE_NOT_SURE, "Not sure"),
    )

    RISK_LOW = "low"
    RISK_MODERATE = "moderate"
    RISK_HIGH = "high"
    RISK_CRITICAL = "critical"
    RISK_CHOICES = (
        (RISK_LOW, "Low"),
        (RISK_MODERATE, "Moderate"),
        (RISK_HIGH, "High"),
        (RISK_CRITICAL, "Critical"),
    )

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"
    GENDER_NOT_SAY = "not_say"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
        (GENDER_NOT_SAY, "Rather not say"),
    )

    class YesNoBoolChoice(Choice):
        Yes = True
        No = False

    class FacilityDestinationChoice(Choice):
        Office = "office"
        Campus = "campus"

    class FacilityDestinationReasonChoice(Choice):
        Staff = "staff"
        Student = "student"
        Visitor = "visitor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    msisdn = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    source = models.CharField(max_length=255)
    province = models.CharField(max_length=6, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=255)
    age = models.CharField(max_length=5, choices=AGE_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    fever = models.BooleanField()
    cough = models.BooleanField()
    sore_throat = models.BooleanField()
    difficulty_breathing = models.BooleanField(null=True, blank=True, default=None)
    exposure = models.CharField(max_length=9, choices=EXPOSURE_CHOICES)
    risk = models.CharField(max_length=8, choices=RISK_CHOICES)
    gender = models.CharField(
        max_length=7, choices=GENDER_CHOICES, blank=True, default=""
    )
    location = models.CharField(max_length=255, blank=True, default="")
    smell = models.BooleanField(null=True, blank=True, default=None)
    preexisting_condition = models.CharField(
        max_length=9, choices=EXPOSURE_CHOICES, blank=True, default=""
    )
    rooms_in_household = models.IntegerField(blank=True, null=True, default=None)
    persons_in_household = models.IntegerField(blank=True, null=True, default=None)
    completed_timestamp = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_by = models.CharField(max_length=255, blank=True, default="")
    confirm_accuracy = models.BooleanField(null=True, blank=True, default=None)
    address = models.CharField(max_length=255, blank=True, default="")
    street_number = models.CharField(max_length=255, blank=True, default="")
    route = models.CharField(max_length=255, blank=True, default="")
    country = models.CharField(max_length=255, blank=True, default="")

    facility_destination = models.CharField(
        choices=FacilityDestinationChoice._choices(),
        max_length=255,
        blank=True,
        default="",
    )
    facility_destination_university = models.ForeignKey(
        University, null=True, blank=True, on_delete=models.CASCADE
    )
    facility_destination_university_other = models.CharField(
        max_length=255, null=True, blank=True
    )
    facility_destination_campus = models.ForeignKey(
        Campus, null=True, blank=True, on_delete=models.CASCADE
    )
    facility_destination_campus_other = models.CharField(
        max_length=255, null=True, blank=True
    )
    facility_destination_reason = models.CharField(
        choices=FacilityDestinationReasonChoice._choices(),
        max_length=255,
        blank=True,
        null=True,
    )
    history_obesity = models.BooleanField(default=False)
    history_diabetes = models.BooleanField(default=False)
    history_hypertension = models.BooleanField(default=False)
    history_cardiovascular = models.BooleanField(default=False)

    @property
    def hashed_msisdn(self):
        return self.msisdn[:3] + "*" * 5 + self.msisdn[-4:]
