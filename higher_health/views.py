from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import HealthCheckLogin, HealthCheckQuestionnaire
from .utils import get_risk_level, save_data


def healthcheck_questionnaire(request):
    if request.method == "POST":
        form = HealthCheckQuestionnaire(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["risk_level"] = get_risk_level(data)
            save_data(data)

            request.session["saved_data"] = data
            return HttpResponseRedirect("/receipt/")
        else:
            print(form.errors)
    else:
        form = HealthCheckQuestionnaire()

    return render(request, "healthcheck_questionnaire.html", {"form": form})


def healthcheck_receipt(request):
    if "saved_data" in request.session:
        data = request.session.get("saved_data")
        del request.session["saved_data"]
        return render(request, "healthcheck_receipt.html", data)
    else:
        return HttpResponseRedirect("/")


def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "healthcheck_receipt.html", {"form": form})


def healthcheck_terms(request, extra_context=None, template=("healthcheck_terms.html")):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
