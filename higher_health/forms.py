from django import forms
from django.forms.widgets import PasswordInput, TextInput

class SimpleForm(forms.Form):
    firstname = forms.CharField(widget=TextInput(attrs={'placeholder': 'First name'}),max_length=100)
    lastname = forms.CharField(widget=TextInput(attrs={'placeholder': 'Last name'}),max_length=100)
