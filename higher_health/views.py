import base64
import hmac
import secrets
import string
from functools import partial
from hashlib import sha256

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms import HealthCheckLogin, HealthCheckOTP, HealthCheckQuestionnaire
from .models import Campus, Covid19Triage, University
from .utils import get_risk_level, save_data


class HealthCheckQuestionnaireView(
    LoginRequiredMixin, UserPassesTestMixin, generic.FormView
):
    login_url = "/login/"
    form_class = HealthCheckQuestionnaire
    template_name = "healthcheck_questionnaire.html"
    success_url = reverse_lazy("healthcheck_receipt")
    raise_exception = False

    def test_func(self):
        return not self.request.user.is_staff

    def form_valid(self, form):
        data = form.cleaned_data
        data["risk_level"] = get_risk_level(data)
        save_data(data, self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(HealthCheckQuestionnaireView, self).get_context_data(**kwargs)
        ctx["campuses"] = partial(
            dict, Campus.objects.values_list("id", "university_id")
        )
        ctx["universities"] = partial(
            dict, University.objects.values_list("id", "province")
        )
        return ctx

    def get_initial(self):
        initial_data = super().get_initial()
        if self.request.method == "GET":
            triage = Covid19Triage.objects.filter(user=self.request.user).last()
            if triage:
                initial_data["msisdn"] = triage.msisdn
                initial_data["first_name"] = triage.first_name
                initial_data["last_name"] = triage.last_name
                initial_data["age_range"] = triage.age
                initial_data["gender"] = triage.gender
                initial_data["address"] = triage.address
                initial_data["city"] = triage.city
                initial_data["street_number"] = triage.street_number
                initial_data["route"] = triage.route
                initial_data["country"] = triage.country

                initial_data["facility_destination"] = triage.facility_destination
                initial_data["facility_destination_province"] = triage.province
                initial_data[
                    "facility_destination_university"
                ] = triage.facility_destination_university_id
                initial_data[
                    "facility_destination_campus"
                ] = triage.facility_destination_campus_id
                initial_data[
                    "facility_destination_reason"
                ] = triage.facility_destination_reason

                initial_data["history_obesity"] = triage.history_obesity
                initial_data["history_diabetes"] = triage.history_diabetes
                initial_data["history_hypertension"] = triage.history_hypertension
                initial_data["history_cardiovascular"] = triage.history_cardiovascular
                initial_data[
                    "history_pre_existing_condition"
                ] = triage.preexisting_condition
        return initial_data


def staff_check(user):
    return not user.is_staff


@login_required
@user_passes_test(staff_check)
def healthcheck_receipt(request):
    triage = Covid19Triage.objects.filter(user=request.user).last()
    if triage:
        data = {
            "risk_level": triage.risk,
            "first_name": triage.first_name,
            "last_name": triage.last_name,
            "timestamp": triage.timestamp,
            "msisdn": triage.hashed_msisdn,
        }
        return render(request, "healthcheck_receipt.html", data)
    return HttpResponseRedirect("/")


class HealthCheckLoginView(generic.FormView):
    form_class = HealthCheckLogin
    template_name = "login.html"
    success_url = reverse_lazy("healthcheck_otp")

    def send_otp_sms(self, user):
        otp = "".join(secrets.choice(string.digits) for _ in range(6))
        h = hmac.new(settings.SECRET_KEY.encode(), otp.encode(), digestmod=sha256)
        otp_hash = base64.b64encode(h.digest()).decode()
        self.request.session["otp_hash"] = otp_hash

        # TODO: send OTP via SMS
        # print(user.username, otp, otp_hash)

    def form_valid(self, form):
        data = form.cleaned_data
        msisdn = data.get("msisdn")
        self.request.session["msisdn"] = msisdn
        user, created = User.objects.get_or_create(username=msisdn)

        self.send_otp_sms(user)
        return super().form_valid(form)


class HealthCheckOTPView(generic.FormView):
    form_class = HealthCheckOTP
    template_name = "otp.html"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if "msisdn" not in request.session:
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.method == "GET" and self.request.session.get("msisdn"):
            msisdn = self.request.session.get("msisdn")
            ctx["hashed_msisdn"] = msisdn[:3] + "*" * 5 + msisdn[-4:]
        return ctx

    def form_valid(self, form):
        msisdn = self.request.session.get("msisdn")
        user = User.objects.get(username=msisdn)
        login(self.request, user)
        return super().form_valid(form)


def healthcheck_terms(request, extra_context=None, template="healthcheck_terms.html"):
    locale_code = request.GET.get("locale")
    return render(request, template, {"locale_code": locale_code})
