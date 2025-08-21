from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import copy
from manager.views import nav_sidebar
from manager.models import Sidebar,LoginPage
from .forms import *
from django.contrib import messages
from .models import *

class LandingEditView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / Secciones"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["sections"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["form"]=LandingForm()
        data["form"].load()

        data["form_title"]="Editar Secciones"
        data["form_submit_label"] = "Guardar"

        return data

    def get(self,request,**kwargs):
        #patient = get_object_or_404(Patient,pk=pk)
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):

        # patient = get_object_or_404(Patient,pk=pk)
        form = LandingForm(request.POST,request.FILES)
        if form.is_valid():
             form.save()
             messages.success(request,"La página se guardo correctamente")
             return redirect('landing-edit')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)
        return redirect('patient-list')

class StepListView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / Secciones"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["sections"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["steps"]=Step.objects.all()
        
        return data

    def get(self,request,**kwargs):
        #patient = get_object_or_404(Patient,pk=pk)
        data = self.make_data()
        return render(request,"page/step_list.html.dtpl",data)

class StepsEditView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self,step):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Pasos - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / Como hacerlo"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["steps"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        
        data["form"]=StepForm(instance=step)
        #data["form"].load()

        data["form_title"]="Editar Paso "+str(step.number)
        data["form_submit_label"] = "Guardar"
        
        return data

    def get(self,request,pk,**kwargs):
        step = get_object_or_404(Step,pk=pk)
        data = self.make_data(step)
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,pk,**kwargs):

        step = get_object_or_404(Step,pk=pk)
        form = StepForm(step,request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Se guardo correctamente")
            return redirect('landing-step-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)
        


class AdvantageListView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / Ventajas"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["advantages"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["advantages"]=Advantage.objects.all()
        
        return data

    def get(self,request,**kwargs):
        #patient = get_object_or_404(Patient,pk=pk)
        data = self.make_data()
        return render(request,"page/advantage_list.html.dtpl",data)

class AdvantageEditView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self,advantage):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / Ventajas"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["advantages"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        
        data["form"]=AdvantageForm(instance=advantage)
        #data["form"].load()

        data["form_title"]="Editar Ventaja "+str(advantage.order)
        data["form_submit_label"] = "Guardar"
        
        return data

    def get(self,request,pk,**kwargs):
        adv = get_object_or_404(Advantage,pk=pk)
        data = self.make_data(adv)
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,pk,**kwargs):

        adv = get_object_or_404(Advantage,pk=pk)
        form = AdvantageForm(adv,request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Se guardo correctamente")
            return redirect('landing-adv-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class FaqListView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / FAQ"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["faq"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["faq"]=FrequentQuestions.objects.all()
        
        return data

    def get(self,request,**kwargs):
        #patient = get_object_or_404(Patient,pk=pk)
        data = self.make_data()
        return render(request,"page/faq_list.html.dtpl",data)

class FaqEditView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self,faq):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / FAQ"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["faq"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        
        data["form"]=FaqForm(instance=faq)
        #data["form"].load()

        data["form_title"]="Editar Pregunta"
        data["form_submit_label"] = "Guardar"
        
        return data

    def get(self,request,pk,**kwargs):
        faq = get_object_or_404(FrequentQuestions,pk=pk)
        data = self.make_data(faq)
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,pk,**kwargs):

        faq = get_object_or_404(FrequentQuestions,pk=pk)
        form = FaqForm(faq,request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Se guardo correctamente")
            return redirect('landing-faq-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class FaqAddView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Editar Landing - Sistema QMM"
        page["content"] = {"title":"Editar Landing","path":["Landing / FAQ"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["landing"]["childs"]["faq"]["active"] = "active"
        sidebar["landing"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        
        data["form"]=FaqForm()
        #data["form"].load()

        data["form_title"]="Agregar Pregunta"
        data["form_submit_label"] = "Agregar"
        
        return data

    def get(self,request,**kwargs):
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):
        form = FaqForm(None,request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Se agrego correctamente")
            return redirect('landing-faq-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class FaqDeleteView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,pk,**kwargs):
        faq = get_object_or_404(FrequentQuestions,pk=pk)
        faq.delete()

        messages.success(request,"La pregunta se borro correctamente")
        return redirect('landing-faq-list')
