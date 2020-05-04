from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from .views import CheckIDNumberView, HealthcheckView, RegistrationViewSet

urlpatterns = [
    path("health", HealthcheckView.as_view(), name="health"),
]
