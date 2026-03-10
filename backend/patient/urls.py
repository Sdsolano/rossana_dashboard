from django.urls import path

from .views import (
    PatientListAPIView,
    PatientDetailAPIView,
    PatientActivateAPIView,
    PatientDeactivateAPIView,
)


urlpatterns = [
    path("patients/", PatientListAPIView.as_view()),
    path("patients/<int:pk>/", PatientDetailAPIView.as_view()),
    path("patients/<int:pk>/activate/", PatientActivateAPIView.as_view()),
    path("patients/<int:pk>/deactivate/", PatientDeactivateAPIView.as_view()),
]

