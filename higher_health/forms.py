from django import forms
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _


class HealthCheckQuestionnaire(forms.Form):
    YES = "yes"
    NO = "no"
    NOT_SURE = "not_sure"

    YES_NO = ((YES, "Yes"), (NO, "No"))

    YES_NO_NOT_SURE = ((YES, "Yes"), (NO, "No"), (NOT_SURE, "Not Sure"))

    age_range = forms.ChoiceField(
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
    latitude = forms.CharField(widget=forms.HiddenInput())
    longitude = forms.CharField(widget=forms.HiddenInput())

    symptoms_sweating = forms.ChoiceField(
        label="Do you feel very hot or cold? Are you sweating or shivering? When you touch your forehead, does it feel hot?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_cough = forms.ChoiceField(
        label="Do you have a cough that recently started?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_sweating = forms.ChoiceField(
        label="Do you feel very hot or cold? Are you sweating or shivering? When you touch your forehead, does it feel hot?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_sore_throat = forms.ChoiceField(
        label="Do you have a sore throat or pain when swallowing?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_breathlessness = forms.ChoiceField(
        label="Do you have breathlessness or a difficulty breathing, that you’ve noticed recently?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_muscles_hurt = forms.ChoiceField(
        label="In the past couple of days, have you experienced pain in your body, especially your muscles hurting more than usual?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_taste = forms.ChoiceField(
        label="Have you noticed any recent changes in your ability to taste or smell things?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )
    medical_exposure = forms.ChoiceField(
        label="Have you been in close contact to someone confirmed to be infected with COVID19?",
        choices=YES_NO_NOT_SURE,
        widget=forms.RadioSelect,
        required=True,
    )
    symptoms_pre_existing_condition = forms.ChoiceField(
        label="Do you have a pre-existing medical condition we should be aware of? (Examples: lung disease, heart disease, diabetes with complications, TB, HIV)",
        choices=YES_NO_NOT_SURE,
        widget=forms.RadioSelect,
        required=True,
    )
    medical_confirm_accuracy = forms.ChoiceField(
        label="Please confirm that the information you shared is accurate to the best of your knowledge and that you give the National Department of Health permission to contact you if necessary?",
        choices=YES_NO,
        widget=forms.RadioSelect,
        required=True,
    )


class HealthCheckLogin(forms.Form):
    phone = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Phone number"}),
        required=True,
        max_length=100,
    )
    fullname = forms.CharField(
        widget=TextInput(attrs={"placeholder": "Last name"}),
        required=True,
        max_length=100,
    )
