from django.urls import path,include
from .views import *


urlpatterns = [
    path('list',ListView.as_view(),name='therapist-list'),
    path('add',AddView.as_view(),name='therapist-add'),
    path('<int:pk>/edit',EditView.as_view(),name='therapist-edit'),
    path('<int:pk>/passwd',PasswordView.as_view(),name='therapist-passwd'),
    path('<int:pk>/delete',DeleteView.as_view(),name='therapist-delete'),
    path('<int:pk>/active',ActiveView.as_view(),name='therapist-active'),
    path('<int:pk>/deactive',DeactiveView.as_view(),name='therapist-deactive'),
    path('api/schedule',ApiScheduleView.as_view(),name='therapist-schedule'),
]
