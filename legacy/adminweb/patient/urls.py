from django.urls import path,include
from .views import *


urlpatterns = [
    path('list',ListView.as_view(),name='patient-list'),
    path('add',AddView.as_view(),name='patient-add'),
    path('<int:pk>/edit',EditView.as_view(),name='patient-edit'),
    path('<int:pk>/delete',DeleteView.as_view(),name='patient-delete'),
    path('<int:pk>/active',ActiveView.as_view(),name='patient-active'),
    path('<int:pk>/deactive',DeactiveView.as_view(),name='patient-deactive'),
]
