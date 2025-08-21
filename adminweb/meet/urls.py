from django.urls import path,include
from .views import *


urlpatterns = [
    path('list',ListView.as_view(),name='meet-list'),
    path('add',CreateView.as_view(),name='meet-add'),

    #path('<int:pk>/edit',EditView.as_view(),name='meet-edit'),
    path('<int:pk>/delete',DeleteView.as_view(),name='meet-delete'),
    path('<int:pk>/send',SendmailView.as_view(),name='meet-sendmail'),

    path('api/clean_temporal',ClearTemporalView.as_view(),name='meet-clean-temporal'),
    path('api/task_sendmails',TaskSendMailView.as_view(),name='meet-task-sendmails'),

    #path('<int:pk>/active',ActiveView.as_view(),name='meet-active'),
    #path('<int:pk>/deactive',DeactiveView.as_view(),name='meet-deactive'),
]
