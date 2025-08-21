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

from .models import *
from .forms import *
# Create your views here.
import copy

class ListView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,**kwargs):
        #global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Pacientes - Sistema QMM"
        page["content"] = {"title":"Pacientes","path":["Pacientes"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["patients"]["active"] = "active"
        data={}
        data["page"]=page
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["nav_sidebar"]=sidebar
        data["patients"]=Patient.objects.all()

        return render(request,"patient/list.html.dtpl",data)

class ActiveView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        patient = get_object_or_404(Patient,pk=pk)
        user = patient.user
        user.is_active = True
        user.save()
        messages.success(request,"El paciente se activo correctamente")
        return redirect('patient-list')

class DeactiveView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        patient = get_object_or_404(Patient,pk=pk)
        user = patient.user
        user.is_active = False
        user.save()
 
        messages.success(request,"El paciente se desactivo correctamente")
        return redirect('patient-list')

class DeleteView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        patient = get_object_or_404(Patient,pk=pk)
        user = patient.user
        patient.delete()
        user.delete()


        messages.success(request,"El paciente se borro correctamente")
        return redirect('patient-list')


class AddView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Agregar Paciente - Sistema QMM"
        page["content"] = {"title":"Agregar paciente","path":["Paciente/Agregar"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["patients"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["form"]=PatientAddForm()
        data["form_title"]="Agregar paciente"
        data["form_submit_label"] = "Agregar"

        return data

    def get(self,request,**kwargs):
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):
        form = PatientAddForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"El paciente se agrego correctamente")
            return redirect('patient-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class EditView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self,patient):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Paciente - Sistema QMM"
        page["content"] = {"title":"Editar paciente","path":["Paciente/Editar"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["patients"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["form"]=PatientEditForm()
        data["form"].load(patient)

        data["form_title"]="Editar paciente"
        data["form_submit_label"] = "Guardar"

        return data

    def get(self,request,pk,**kwargs):
        patient = get_object_or_404(Patient,pk=pk)
        data = self.make_data(patient)
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,pk,**kwargs):
        patient = get_object_or_404(Patient,pk=pk)
        form = PatientEditForm(request.POST,request.FILES)
        if form.is_valid():
            form.save(patient)
            messages.success(request,"La paciente se guardo correctamente")
            return redirect('patient-list')
        else:
            data = self.make_data(patient)
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)