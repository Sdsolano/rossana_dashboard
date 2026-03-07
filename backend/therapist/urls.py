from django.urls import path
from .views import (
    TherapistListAPIView,
    ScheduleConfigAPIView,
    TherapistDetailAPIView,
    TherapistPasswordAPIView,
    TherapistActivateAPIView,
    TherapistDeactivateAPIView,
    TherapistAvailabilityAPIView,
    TherapistFreedaysAPIView,
    AuthLoginAPIView,
    MeAPIView,
    MeAvailabilityAPIView,
    TherapistGenerateScheduleAPIView,
)

urlpatterns = [
    path("therapists/", TherapistListAPIView.as_view()),
    path("therapists/<int:pk>/", TherapistDetailAPIView.as_view()),
    path("therapists/<int:pk>/password/", TherapistPasswordAPIView.as_view()),
    path("therapists/<int:pk>/activate/", TherapistActivateAPIView.as_view()),
    path("therapists/<int:pk>/deactivate/", TherapistDeactivateAPIView.as_view()),
    path("therapists/<int:pk>/availability/", TherapistAvailabilityAPIView.as_view()),
    path("therapists/<int:pk>/freedays/", TherapistFreedaysAPIView.as_view()),
    path("therapists/<int:pk>/generate-schedule/", TherapistGenerateScheduleAPIView.as_view()),
    path("auth/login/", AuthLoginAPIView.as_view()),
    path("me/", MeAPIView.as_view()),
    path("me/availability/", MeAvailabilityAPIView.as_view()),
    path("schedule-config/", ScheduleConfigAPIView.as_view()),
]
