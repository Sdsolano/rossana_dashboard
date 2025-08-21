from django.urls import path,include

from .views import Login,LogoutView,Dashboard,ConfigView
#from .views import SheetAdd,SheetList,SheetActive,SheetDeactive,SheetEdit,SheetDelete
#from .views import OrderList,ClientList
#from .views import CategorieList,CategorieAdd,CategorieEdit,CategorieDelete
from patient.views import ListView as PatientList


urlpatterns = [
    path('',Dashboard.as_view(),name='manager-dashboard'),
    #path('',PatientList.as_view(),name='manager-dashboard'),

    #path('',SheetList.as_view(),name='manager-dashboard'),
    #path('billing/',Dashboard.as_view(),name='manager-billing'),
    #path('products/',ProductList.as_view(),name='manager-products'),
    #path('products/add',ProductAdd.as_view(),name='manager-product-add'),

    #path('sheets/',SheetList.as_view(),name='manager-sheets'),
    #path('sheets/add',SheetAdd.as_view(),name='manager-sheet-add'),
    #path('sheets/<int:pk>/edit',SheetEdit.as_view(),name='manager-sheet-edit'),
    #path('sheets/<int:pk>/delete',SheetDelete.as_view(),name='manager-sheet-delete'),
    #path('sheets/<int:pk>/active',SheetActive.as_view(),name='manager-sheet-active'),
    #path('sheets/<int:pk>/deactive',SheetDeactive.as_view(),name='manager-sheet-deactive'),

    path('patients/',include('patient.urls')),
    path('therapist/',include('therapist.urls')),
    path('meets/',include('meet.urls')),
    path('pays/',include('pay.urls')),
    path('page/',include('page.urls')),

    #path('categories/',CategorieList.as_view(),name='manager-cat'),
    #path('categories/add',CategorieAdd.as_view(),name='manager-cat-add'),
    #path('categories/<int:pk>/edit',CategorieEdit.as_view(),name='manager-cat-edit'),
    #path('categories/<int:pk>/delete',CategorieDelete.as_view(),name='manager-cat-delete'),
    #path('orders/',OrderList.as_view(),name='manager-orders'),
    #path('clients/',ClientList.as_view(),name='manager-clients'),
    #path('orders/add',OrderAdd.as_view(),name='manager-order-add'),
    path('login/', Login.as_view(), name='manager-login'),
    path('logout/', LogoutView.as_view(), name='manager-logout'),
    path('config/', ConfigView.as_view(), name='manager-config')
]
