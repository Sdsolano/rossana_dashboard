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

from .models import *
from .forms import *

import copy
#from datetime import datetime

class ListView(ManagerView):
    
    def get(self,request,**kwargs):
        #global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Citas - Sistema QMM"
        page["content"] = {"title":"Citas","path":["Citas"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["meets"]["active"] = "active"
        data={}
        data["page"]=page
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["nav_sidebar"]=sidebar

        if "filter" in request.GET:
            filter_data = request.GET["filter"]
        else:
            filter_data = ""

        if filter_data == "today":
            data["meets"]=Meet.objects.filter(created__gte=timezone.now().date())
        elif filter_data == "yesterday":
            data["meets"]=Meet.objects.filter(created__gte=(timezone.now().date() - timedelta(days=1)),created__lt=timezone.now().date())
        elif filter_data == "last7days":
            data["meets"]=Meet.objects.filter(created__gte=(timezone.now().date() - timedelta(days=7)))
        elif filter_data == "lastmonth":
            data["meets"]=Meet.objects.filter(created__gte=(timezone.now().date() - timedelta(days=30)))
        elif filter_data == "all":
            data["meets"]=Meet.objects.all()
        else:
            data["meets"]=Meet.objects.filter(created__gte=timezone.now().date())

        if "order" in request.GET:
            order = request.GET["order"]
        else:
            order = ""

        if order == "status":
            data["meets"] = data["meets"].order_by("status")
        else:
            data["meets"] = data["meets"].order_by("-created")

        data["meets"] = data["meets"].exclude(status="F").exclude(status="T")

        return render(request,"meet/list.html.dtpl",data)

    



class DeleteView(ManagerView):
    def get(self,request,pk,**kwargs):
        meet = get_object_or_404(Meet,pk=pk)
        meet.delete()
        
        messages.success(request,"La cita fue borrada")
        return redirect('meet-list')


class CreateView(ManagerView):
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Nueva cita - Sistema QMM"
        page["content"] = {"title":"Nuevo cita","path":["Cita/Nueva"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["meets"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["form"]=MeetCreateForm()
        data["form_title"]="Nueva cita"
        data["form_submit_label"] = "Guardar"

        return data

    def get(self,request,**kwargs):
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):
        form = MeetCreateForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"La cita se creo correctamente")
            return redirect('meet-list')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)


class SendmailView(ManagerView):
    
    def get(self,request,pk,**kwargs):
        meet = get_object_or_404(Meet,pk=pk)
        if meet.send_emails() == 1:
            messages.success(request,"El email se envió correctamente.")
        else:
            messages.error(request,"Ocurrio un error al intentar enviar el email.")

        return redirect('meet-list')

class ClearTemporalView(View):
    
    def get(self,request,**kwargs):
        Meet.remove_temporals()
        return HttpResponse('<h1>TodoOK!</h1>')

class TaskSendMailView(View):
    
    def get(self,request,**kwargs):
        list_of_meets = Meet.objects.filter(status="D",date__gte=timezone.now())
        emails_sended = 0
        for m in list_of_meets:
            delta = m.ct_email_patient_remember
            m.task_send_email_remember()
            delta = m.ct_email_patient_remember - delta
            emails_sended += delta

        list_of_meets = Meet.objects.filter(status="D",date__gte=timezone.now())
        emails_sended = 0
        for m in list_of_meets:
            delta = m.ct_email_patient_remember
            m.task_send_email_remember()
            delta = m.ct_email_patient_remember - delta
            emails_sended += delta



        return HttpResponse(f'<h1>Enviados {emails_sended} mails</h1>')

