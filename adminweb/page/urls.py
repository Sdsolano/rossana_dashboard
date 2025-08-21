from django.urls import path,include
from .views import *


urlpatterns = [
    path('edit',LandingEditView.as_view(),name='landing-edit'),
    path('steps',StepListView.as_view(),name='landing-step-list'),
    path('step/<int:pk>/',StepsEditView.as_view(),name='landing-step-edit'),
    path('advantages',AdvantageListView.as_view(),name='landing-adv-list'),
    path('advantages/<int:pk>/',AdvantageEditView.as_view(),name='landing-adv-edit'),
    path('faq',FaqListView.as_view(),name='landing-faq-list'),
    path('faq/new/',FaqAddView.as_view(),name='landing-faq-add'),
    path('faq/<int:pk>/edit',FaqEditView.as_view(),name='landing-faq-edit'),
    path('faq/<int:pk>/delete',FaqDeleteView.as_view(),name='landing-faq-delete'),
    #path('add',CreateView.as_view(),name='meet-add'),

    #path('<int:pk>/edit',EditView.as_view(),name='meet-edit'),
    #path('<int:pk>/active',ActiveView.as_view(),name='meet-active'),
    #path('<int:pk>/deactive',DeactiveView.as_view(),name='meet-deactive'),
]
