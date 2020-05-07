from django.shortcuts import render

from .forms import HealthCheckQuestionnaire, HealthCheckLogin


def healthcheck_questionnaire(request):
    form = HealthCheckQuestionnaire()
    return render(request, "healthcheck_questionnaire.html", {"form": form})

def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "healthcheck_login.html", {"form": form})

def healthcheck_terms(
        request,
        extra_context=None,
        template=('healthcheck_terms.html')):
    locale_code = request.GET.get('locale')
    return render(request, template, {'locale_code': locale_code})
