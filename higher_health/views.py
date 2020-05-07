from django.shortcuts import render

from django.http import HttpResponseRedirect
from .forms import HealthCheckQuestionnaire, HealthCheckLogin



def healthcheck_questionnaire(request):
    submitted = False
    if request.method == 'POST':
        form = HealthCheckQuestionnaire(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # assert False
            return HttpResponseRedirect('/?submitted=True')
    else:
        form = HealthCheckQuestionnaire()
        if 'submitted' in request.GET:
            submitted = True
            # raise FieldError(e[0])
    return render(request, "healthcheck_questionnaire.html", {"form": form, "submitted": submitted })

def healthcheck_login(request):
    form = HealthCheckLogin()
    return render(request, "healthcheck_login.html", {"form": form})

def healthcheck_terms(
        request,
        extra_context=None,
        template=('healthcheck_terms.html')):
    locale_code = request.GET.get('locale')
    return render(request, template, {'locale_code': locale_code})
