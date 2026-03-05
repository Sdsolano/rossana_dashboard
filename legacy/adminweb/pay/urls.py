from django.urls import path,include
from .views import *


urlpatterns = [
    path('list',ListView.as_view(),name='pay-list'),
    path('add',CreateView.as_view(),name='pay-add'),
    #path('<int:pk>/edit',EditView.as_view(),name='meet-edit'),
    path('<int:pk>/delete',DeleteView.as_view(),name='pay-delete'),

    #path('<int:pk>/active',ActiveView.as_view(),name='meet-active'),
    #path('<int:pk>/deactive',DeactiveView.as_view(),name='meet-deactive'),
]
