from django.urls import path

from . import views

urlpatterns = [
    path("", views.healthcheck_questionnaire, name="healthcheck_questionnaire"),
    path("receipt/", views.healthcheck_receipt, name="healthcheck_receipt"),
    path("login/", views.healthcheck_login, name="healthcheck_login"),
    path("terms/", views.healthcheck_terms, name="healthcheck_terms"),
]
