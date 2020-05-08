from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import HealthCheckLogin, HealthCheckQuestionnaire
from .utils import get_risk_level, save_data


def healthcheck_questionnaire(request):
    submitted = False
    if request.method == "POST":
        form = HealthCheckQuestionnaire(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            risk_level = get_risk_level(data)
            save_data(data, risk_level)
            return HttpResponseRedirect(f"/?submitted=True&risk_level={risk_level}")
        else:
            # TODO: need to handle this
            print(form.errors)
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
    return render(request, "healthcheck_login.html", {"form": form})


def healthcheck_terms(request, extra_context=None, template=("healthcheck_terms.html")):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
