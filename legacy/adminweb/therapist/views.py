from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Min, Sum
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils import timezone
from django.http import Http404,HttpResponse

from manager.views import nav_sidebar,ManagerView
from manager.models import Sidebar,LoginPage
from manager.forms import UserPasswordForm

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
        page["title"] = "Terapeutas - Sistema QMM"
        page["content"] = {"title":"Terapeutas","path":["Terapeutas"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["therapist"]["active"] = "active"
        data={}
        data["page"]=page
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["nav_sidebar"]=sidebar
        data["therapist"]=Therapist.objects.all()

        return render(request,"therapist/list.html.dtpl",data)

class ActiveView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        therapist = get_object_or_404(Therapist,pk=pk)
        user = therapist.user
        user.is_active = True
        user.save()
        messages.success(request,"El terapeuta se activo correctamente")
        return redirect('therapist-list')

class DeactiveView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        therapist = get_object_or_404(Therapist,pk=pk)
        user = therapist.user
        user.is_active = False
        user.save()
 
        messages.success(request,"El terapeuta se desactivo correctamente")
        return redirect('therapist-list')

class DeleteView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        therapist = get_object_or_404(Therapist,pk=pk)
        user = therapist.user
        therapist.delete()
        user.delete()


        messages.success(request,"El terapeuta se borro correctamente")
        return redirect('therapist-list')


class AddView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Agregar Terapeuta - Sistema QMM"
        page["content"] = {"title":"Agregar terapeuta","path":["Terapeuta/Agregar"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["therapist"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["form"]=TherapistAddForm()
        data["form_title"]="Agregar terapeuta"
        data["form_submit_label"] = "Agregar"

        return data

    def get(self,request,**kwargs):
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):
        form = TherapistAddForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"El terapeuta se agrego correctamente")
            return redirect('therapist-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class EditView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self,therapist):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Terapeuta - Sistema QMM"
        page["content"] = {"title":"Editar terapeuta","path":["Terapeuta/Editar"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["therapist"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["form"]=TherapistEditForm()
        data["form"].load(therapist)

        data["form_title"]="Editar terapeuta"
        data["form_submit_label"] = "Guardar"

        return data

    def get(self,request,pk,**kwargs):
        therapist = get_object_or_404(Therapist,pk=pk)
        data = self.make_data(therapist)
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,pk,**kwargs):
        therapist = get_object_or_404(Therapist,pk=pk)
        form = TherapistEditForm(request.POST,request.FILES)
        if form.is_valid():
            form.save(therapist)
            messages.success(request,"El terapeuta se guardo correctamente")
            return redirect('therapist-list')
        else:
            data = self.make_data(therapist)
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class PasswordView(ManagerView):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Contraseña"
        page["content"] = {"title":"Editar terapeuta","path":["Terapeuta/Contraseña"]}
        

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["therapist"]["active"] = "active"
        
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        return data

    def get(self,request,pk,**kwargs):
        data = self.make_data()
        form = UserPasswordForm()
        data["form"]=form
        data["form_title"]="Cambiar Contraseña"
        data["form_submit_label"] = "Guardar"
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,pk,**kwargs):
        therapist = get_object_or_404(Therapist,pk=pk)
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            form.save(therapist.user)
            messages.success(request,"Se cambio la contraseña correctamente")
            return redirect('therapist-list')
        else: # si no es valido vuelve a cargar el formulario y muestar el error
            data = self.make_data()
            data["form"] = form
            data["form_title"]="Actualizar Contraseña"
            data["form_submit_label"] = "Guardar"
            return render(request,"manager/form_as_p_data.html.dtpl",data)

class ApiScheduleView(View):
    def get(self,request,**kwargs):
        config = Config.objects.get(name="default")
        for t in Therapist.objects.filter(user__is_active=True):
            dt_now = pytz.timezone(t.timezone_verbose).normalize(timezone.now())
            t.make_schedule(dt_now,3,config.rate)
        return HttpResponse(f'<h1>Schedule! {len(t.meet_set.filter(status="F"))}</h1>')
