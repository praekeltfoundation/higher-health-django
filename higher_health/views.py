from .forms import LocationCheckerForm, PersonalInfoForm, LoginForm
from django.shortcuts import render

def healthcheck_location(request):
    form = LocationCheckerForm()
    return render(request, 'health-check_location-questionnaire.html', {'form': form})

def healthcheck_personalInfo(request):
    form = PersonalInfoForm()
    return render(request, 'health-check_personal-info.html', {'form': form})

def healthcheck_login(request):
    form = LoginForm()
    return render(request, 'health-check_login.html', {'form': form})
