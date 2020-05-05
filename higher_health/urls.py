from django.urls import path

from . import views

urlpatterns = [
    path('', views.form_new, name='form_new'),
]
