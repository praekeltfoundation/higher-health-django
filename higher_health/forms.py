from django import forms
from django.forms.widgets import PasswordInput, TextInput
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class HealthCheckQuestionnaire(forms.Form):
    ageRange = forms.ChoiceField(
        label="How old are you?",
        choices=(
            ("", _("Age")),
            ("<18", _("<18")),
            ("18-39", _("18-39")),
            ("40-65", _("40-65")),
            (">65", _(">65")),
        ),
        required=True,
    )

    gender = forms.ChoiceField(
        label="Please provide us with the gender you identify as",
        choices=(
            ("", _("Gender")),
            ("Male", _("Male")),
            ("Female", _("Female")),
            ("Other", _("Other")),
            ("Rather not say", _("Rather not say")),
        ),
        required=True,
    )
    province = forms.ChoiceField(
        label="In which Province are you currently residing?",
        choices=(
            ("", _("Province")),
            ("Eastern Cape", _("Eastern Cape")),
            ("Free State", _("Free State")),
            ("Gauteng", _("Gauteng")),
            ("KwaZulu Natal", _("KwaZulu Natal")),
            ("Limpopo", _("Limpopo")),
            ("Mpumalanga", _("Mpumalanga")),
            ("North West", _("North West")),
            ("Northern Cape", _("Northern Cape")),
            ("Western Cape", _("Western Cape")),
        ),
        required=True,
    )

class HealthCheckLogin(forms.Form):
    phone = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Phone number"}),required=True, max_length=100
    )
    fullname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Last name"}),required=True, max_length=100
    )
