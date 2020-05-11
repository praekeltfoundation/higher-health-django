from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import HealthCheckLogin, HealthCheckQuestionnaire
from .models import Covid19Triage
from .utils import get_risk_level, save_data


def healthcheck_questionnaire(request):
    if request.method == "POST":
        form = HealthCheckQuestionnaire(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["risk_level"] = get_risk_level(data)
            triage = save_data(data)

            request.session["triage_id"] = str(triage.id)
            return HttpResponseRedirect("/receipt/")
        else:
            print(form.errors)
    else:
        initial_data = {}
        try:
            if "triage_id" in request.session:
                triage = Covid19Triage.objects.get(id=request.session["triage_id"])
                initial_data["msisdn"] = triage.msisdn
                initial_data["first_name"] = triage.first_name
                initial_data["last_name"] = triage.last_name
                initial_data["age_range"] = triage.age
                initial_data["gender"] = triage.gender
                initial_data["province"] = triage.province
                initial_data["address"] = triage.address
                initial_data["city"] = triage.city
                initial_data["street_number"] = triage.street_number
                initial_data["route"] = triage.route
                initial_data["country"] = triage.country
        except Covid19Triage.DoesNotExist:
            pass

        form = HealthCheckQuestionnaire(initial=initial_data)

    return render(request, "healthcheck_questionnaire.html", {"form": form})


def healthcheck_receipt(request):
    try:
        if "triage_id" in request.session:
            triage = Covid19Triage.objects.get(id=request.session["triage_id"])
            data = {
                "risk_level": triage.risk,
                "first_name": triage.first_name,
                "last_name": triage.last_name,
                "timestamp": triage.timestamp,
                "msisdn": triage.hashed_msisdn,
            }
            return render(request, "healthcheck_receipt.html", data)
    except Covid19Triage.DoesNotExist:
        pass

    return HttpResponseRedirect("/")


def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "healthcheck_receipt.html", {"form": form})


def healthcheck_terms(request, extra_context=None, template=("healthcheck_terms.html")):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
