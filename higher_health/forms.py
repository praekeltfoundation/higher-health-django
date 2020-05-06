from django import forms
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _


class LocationCheckerForm(forms.Form):
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
        required=False,
    )


class PersonalInfoForm(forms.Form):
    firstname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "First name"}), max_length=100
    )
    lastname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Last name"}), max_length=100
    )


class LoginForm(forms.Form):
    firstname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "First name"}), max_length=100
    )
    lastname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Last name"}), max_length=100
    )
