from django.urls import path

from .views import PageListAPIView, PageDetailAPIView, PagePublicDetailAPIView

urlpatterns = [
    path("pages/", PageListAPIView.as_view()),
    path("pages/<int:pk>/", PageDetailAPIView.as_view()),
    path("public/pages/<slug:slug>/", PagePublicDetailAPIView.as_view()),
]

