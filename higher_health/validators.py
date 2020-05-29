import phonenumbers
from django.forms import ValidationError


def za_phone_number(value):
    try:
        number = phonenumbers.parse(value, "ZA")
    except phonenumbers.NumberParseException as e:
        raise ValidationError(str(e))
    if not phonenumbers.is_possible_number(number):
        raise ValidationError("Not a possible phone number")
    if not phonenumbers.is_valid_number(number):
        raise ValidationError("Not a valid phone number")

    if str(number.country_code) != "27":
        raise ValidationError("Only South African numbers are allowed")
    if len(str(number.national_number)) != 9:
        raise ValidationError("Please enter a valid 10-digit phone number")
