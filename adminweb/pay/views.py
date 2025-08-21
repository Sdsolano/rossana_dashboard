from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Min, Sum
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils import timezone


from manager.views import nav_sidebar,ManagerView
from manager.models import Sidebar,LoginPage


from meet.models import Pay
from .models import *
from .forms import *

import copy
from datetime import datetime

class ListView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,**kwargs):
        #global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Pagos - Sistema QMM"
        page["content"] = {"title":"Pagos","path":["Pagos"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["pays"]["active"] = "active"
        data={}
        data["page"]=page
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["nav_sidebar"]=sidebar
        data["pays"]=Pay.objects.all().order_by("-timestamp")

        return render(request,"pay/list.html.dtpl",data)


class DeleteView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        pay = get_object_or_404(Pay,pk=pk)
        pay.delete()
        
        messages.success(request,"El pago fue borrado")
        return redirect('pay-list')


class CreateView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Nuevo pago - Sistema QMM"
        page["content"] = {"title":"Nuevo pago","path":["pago/Nuevo"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["meets"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["form"]=MeetCreateForm()
        data["form_title"]="Nuevo pago"
        data["form_submit_label"] = "Guardar"

        return data

    def get(self,request,**kwargs):
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):
        form = MeetCreateForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"El pago se creo correctamente")
            return redirect('meet-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


