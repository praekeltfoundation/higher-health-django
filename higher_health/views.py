from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import HealthCheckLogin, HealthCheckQuestionnaire
from .utils import get_risk_level, save_data


def healthcheck_questionnaire(request):
    if request.method == "POST":
        form = HealthCheckQuestionnaire(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            risk_level = get_risk_level(data)
            save_data(data, risk_level)

            request.session["risk_level"] = risk_level
            return HttpResponseRedirect("/receipt/")
        else:
            # TODO: need to handle this
            print(form.errors)
    else:
        form = HealthCheckQuestionnaire()

    return render(request, "healthcheck_questionnaire.html", {"form": form})


def healthcheck_receipt(request):
    if "risk_level" in request.session:
        risk_level = request.session.get("risk_level")
        del request.session["risk_level"]
        return render(request, "includes/receipt.html", {"risk_level": risk_level})
    else:
        return HttpResponseRedirect("/")


def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "includes/receipt.html", {"form": form})


def healthcheck_terms(request, extra_context=None, template=("healthcheck_terms.html")):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
