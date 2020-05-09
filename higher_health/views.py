from datetime import datetime

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
        # TODO: Prepopulate profile data if triage_id in session
        form = HealthCheckQuestionnaire()

    return render(request, "healthcheck_questionnaire.html", {"form": form})


def healthcheck_receipt(request):
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
    else:
        return HttpResponseRedirect("/")


def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "healthcheck_receipt.html", {"form": form})


def healthcheck_terms(request, extra_context=None, template=("healthcheck_terms.html")):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
