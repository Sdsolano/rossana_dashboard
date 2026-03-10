from django.urls import path

from .views import PayListAPIView, PayDetailAPIView, PayConfirmAPIView

urlpatterns = [
    path("pays/", PayListAPIView.as_view()),
    path("pays/<int:pk>/", PayDetailAPIView.as_view()),
    path("pays/<int:pk>/confirm/", PayConfirmAPIView.as_view()),
]

