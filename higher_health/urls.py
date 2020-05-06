from django.urls import path

from . import views

urlpatterns = [
    path("", views.healthcheck_location, name="healthcheck_location"),
    path("", views.healthcheck_personalInfo, name="healthcheck_personalInfo"),
    path("", views.healthcheck_login, name="healthcheck_login"),
]
