from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.HealthCheckQuestionnaireView.as_view(),
        name="healthcheck_questionnaire",
    ),
    path("receipt/", views.healthcheck_receipt, name="healthcheck_receipt"),
    path("login/", views.healthcheck_login, name="healthcheck_login"),
    path("terms/", views.healthcheck_terms, name="healthcheck_terms"),

    path('ajax/campuses/', views.load_campuses, name='ajax_load_campuses'),
    path('ajax/universities/', views.load_universities, name='ajax_load_universities')
]
