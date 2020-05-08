from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import HealthCheckLogin, HealthCheckQuestionnaire
from .utils import get_risk_level


def healthcheck_questionnaire(request):
    submitted = False
    if request.method == "POST":
        form = HealthCheckQuestionnaire(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            risk_level = get_risk_level(cd)
            return HttpResponseRedirect(f"/?submitted=True&risk_level={risk_level}")
    else:
        form = HealthCheckQuestionnaire()
        if "submitted" in request.GET:
            submitted = True

    return render(
        request,
        "healthcheck_questionnaire.html",
        {"form": form, "submitted": submitted},
    )


def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "includes/receipt.html", {"form": form})


def healthcheck_terms(request, extra_context=None, template=("healthcheck_terms.html")):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
