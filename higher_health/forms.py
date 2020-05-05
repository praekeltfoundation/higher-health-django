from django import forms
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _

class LocationCheckerForm(forms.Form):
    ageRange = forms.ChoiceField(
        label="How old are you?",
        choices= (
            ('', _('Age')),
            ('<18', _('<18')),
            ('18-39', _('18-39')),
            ('40-65', _('40-65')),
            ('>65', _('>65'))
        ),
        required=True
    )
    gender = forms.ChoiceField(
        label="Please provide us with the gender you identify as",
        choices= (
            ('', _('Gender')),
            ('Male', _('Male')),
            ('Female', _('Female')),
            ('Other', _('Other')),
            ('Rather not say', _('Rather not say'))
        ),
        required=True
    )
    province = forms.ChoiceField(
        label="In which Province are you currently residing?",
        choices= (
            ('', _('Province')),
            ('Eastern Cape', _('Eastern Cape')),
            ('Free State', _('Free State')),
            ('Gauteng', _('Gauteng')),
            ('KwaZulu Natal', _('KwaZulu Natal')),
            ('Limpopo', _('Limpopo')),
            ('Mpumalanga', _('Mpumalanga')),
            ('North West', _('North West')),
            ('Northern Cape', _('Northern Cape')),
            ('Western Cape', _('Western Cape')),
        ),
        required=False
    )
    provinceType = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'Which Province are you currently residing?'}),max_length=100)
    residenceLocation = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'Name of your Suburb, Township, Town or Village (or nearest)'}),max_length=100)
    locationPin = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'Please share your location using (Or SKIP if you are unable to)','helpText':'This will help us to more accurately map cases of COVID-19'}),max_length=100)


class MedicalCheckerForm(forms.Form):
    firstname = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'First name'}),max_length=100)
    lastname = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'Last name'}),max_length=100)

class PersonalInfoForm(forms.Form):
    firstname = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'First name'}),max_length=100)
    lastname = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'Last name'}),max_length=100)

class LoginForm(forms.Form):
    firstname = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'First name'}),max_length=100)
    lastname = forms.CharField(widget=TextInput(attrs={'class':'textInputs','placeholder': 'Last name'}),max_length=100)
