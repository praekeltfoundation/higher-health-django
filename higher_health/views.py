from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from .forms import HealthCheckLogin, HealthCheckQuestionnaire
from .models import Covid19Triage
from .utils import get_risk_level, save_data


class HealthCheckQuestionnaireView(generic.FormView):
    form_class = HealthCheckQuestionnaire
    template_name = "healthcheck_questionnaire.html"
    success_url = reverse_lazy('healthcheck_receipt')

    def form_valid(self, form):
        data = form.cleaned_data
        data["risk_level"] = get_risk_level(data)
        triage = save_data(data)
        self.request.session["triage_id"] = str(triage.id)
        return super().form_valid(form)

    def get_initial(self):
        initial_data = super().get_initial()
        if self.request.session.get("triage_id"):
            triage = get_object_or_404(Covid19Triage, id=self.request.session["triage_id"])

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

            initial_data["facility_destination"] = triage.facility_destination
            initial_data["facility_destination_province"] = triage.facility_destination_province
            initial_data["facility_destination_university"] = triage.facility_destination_university
            initial_data["facility_destination_campus"] = triage.facility_destination_campus
            initial_data["facility_destination_reason"] = triage.facility_destination_reason

            initial_data["history_obesity"] = triage.history_obesity
            initial_data["history_diabetes"] = triage.history_diabetes
            initial_data["history_hypertension"] = triage.history_hypertension
            initial_data["history_cardiovascular"] = triage.history_cardiovascular
            initial_data["history_other"] = triage.history_other
        return initial_data


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
