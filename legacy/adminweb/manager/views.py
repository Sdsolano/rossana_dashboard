from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Min, Sum
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils import timezone
from django.db.models import Q

#from product.models import Product,Categorie
#from product.forms import ProductForm, SheetProductForm,CategorieForm

#from order.models import Order,Client
from patient.models import Patient
from therapist.models import Therapist
from meet.models import Meet,Pay



from manager.models import Sidebar,LoginPage
from manager.forms import ConfigForm

from datetime import datetime,timedelta
# Create your views here.
import copy

nav_sidebar = {"dashboard":{
                        "name":"Panel de control",
                        "icon":"fas fa-tachometer-alt",
                        "href":reverse_lazy("manager-dashboard"),
                        "active":"no",
                        "hide":False

                    },
                
                "patients":{
                        "name":"Pacientes",
                        "icon":"fas fa-user-injured",
                        "href":reverse_lazy("patient-list"),
                        "active":"no",
                        "hide":False
                    },
                "therapist":{
                        "name":"Terapeutas",
                        "icon":"fas fa-user-md",
                        "href":reverse_lazy("therapist-list"),
                        "active":"no",
                        "hide":False
                    },
                "meets":{
                         "name":"Citas",
                         "icon":"fas fa-calendar-day",
                         "href":reverse_lazy("meet-list"),
                         "active":"no",
                         "hide":False
                     },
                "pays":{
                         "name":"Pagos",
                         "icon":"fas fa-credit-card",
                         "href":reverse_lazy("pay-list"),
                         "active":"no",
                         "hide":False
                     },
                "s1":{
                         "name":"CONFIGURACION",
                         "header":True
                     },
                "landing":{
                        "name":"Landing",
                        "icon":"fas fa-file-code",
                        "href":reverse_lazy("manager-dashboard"),
                        "active":"no",
                        "hide":False,
                        "childs":{
                                    "sections":{
                                                    "name":"Secciones",
                                                    "icon":"",
                                                    "href":reverse_lazy("landing-edit"),
                                                    "active":"no",
                                                    "hide":True

                                                },
                                    "steps":{
                                                    "name":"Como hacerlo",
                                                    "icon":"",
                                                    "href":reverse_lazy("landing-step-list"),
                                                    "active":"no",
                                                    "hide":True

                                                },
                                    "advantages":{
                                                    "name":"Ventajas",
                                                    "icon":"",
                                                    "href":reverse_lazy("landing-adv-list"),
                                                    "active":"no",
                                                    "hide":True

                                                },
                                    "faq":{
                                                "name":"Preguntas frecuentes",
                                                "icon":"",
                                                "href":reverse_lazy("landing-faq-list"),
                                                "active":"no",
                                                "hide":True

                                            },

                        }

                    },
                "config":{
                        "name":"Configuración",
                        "icon":"fas fa-cog",
                        "href":reverse_lazy("manager-config"),
                        "active":"no",
                        "hide":False
                    },
            }



class Login(View):
    def get(self,request,**kwargs):
        page = {}
        login = LoginPage.objects.get(name="root")
        page["title"] = "Login"
        #login["title"] = "N3SYSTEM"
        return render(request,"manager/login.html",{"page":page,"login":login})

    def post(self,request,**kargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(self.request,user)
            if 'next' in self.request.GET:
                return redirect(self.request.GET['next'])
            return redirect('manager-dashboard')

        else:
            messages.error(self.request, 'Usuario o contraseña incorrecto')
            return redirect('manager-login')


class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect("manager-login")

class ManagerView(LoginRequiredMixin,UserPassesTestMixin,View):
    login_url = reverse_lazy("manager-login")

    def test_func(self):
        return not self.request.user.groups.filter(name="therapist").exists()


class Dashboard(ManagerView):
    
    def get(self,request,**kwargs):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Panel de control - Sistema QMM"
        page["content"] = {"title":"Panel de control","path":["Panel de control"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        sidebar["dashboard"]["active"] = "active"
        data={}
        data["page"]=page
        data["sidebar"] = Sidebar.objects.get(name="root")
        data["nav_sidebar"]=sidebar
        #data["orders_pending"] = len(Order.objects.filter(status="P"))
        data["meets_month"] = len(Meet.objects.filter(Q(status="D") | Q(status="R"),created__gte=timezone.now().date()-timedelta(days=timezone.now().date().day)))
        data["patients"] = len(Patient.objects.all())
        data["therapist"] = len(Therapist.objects.filter(user__is_active=True))

        pays = Pay.objects.filter(status="D",timestamp__gte=timezone.now().date()-timedelta(days=timezone.now().date().day))
        pays = [p.amount for p in pays]

        data["billing"] = sum(pays)

        return render(request,"manager/dashboard.html.dtpl",data)


class ConfigView(ManagerView):
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Configuración - Sistema QMM"
        page["content"] = {"title":"Configuración","path":["Configuración"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        #sidebar["landing"]["childs"]["sections"]["active"] = "active"
        sidebar["config"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        data["form"]=ConfigForm()
        data["form"].load()

        data["form_title"]="Configuración"
        data["form_submit_label"] = "Guardar"

        return data

    def get(self,request,**kwargs):
        #patient = get_object_or_404(Patient,pk=pk)
        data = self.make_data()
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):

        # patient = get_object_or_404(Patient,pk=pk)
        form = ConfigForm(request.POST,request.FILES)
        if form.is_valid():
             form.save()
             messages.success(request,"La configuración se guardo correctamente")
             return redirect('manager-config')
        else:
            data = self.make_data()
            data["form"] = form
            return render(request,"manager/form_as_p_data.html.dtpl",data)
        return redirect('patient-list')


class UserPasswordView(ManagerView):
    
    def make_data(self):
        global nav_sidebar
        page = {}
        #nav_sidebar = {}
        page["title"] = "Contraseña"
        page["content"] = {"title":"Contraseña","path":["Usuario - Contraseña"]}
        #login["title"] = "N3SYSTEM"

        sidebar = copy.deepcopy(nav_sidebar)
        #sidebar["supervisors"]["active"] = "active"
        data={}
        data["page"]=page
        data["nav_sidebar"]=sidebar
        data["sidebar"] = Sidebar.objects.get(name="root")

        return data

    def get(self,request,**kwargs):
        data = self.make_data()
        form = UserPasswordForm()
        data["form"]=form
        data["form_title"]="Cambiar Contraseña"
        data["form_submit_label"] = "Guardar"
        return render(request,"manager/form_as_p_data.html.dtpl",data)

    def post(self,request,**kwargs):
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request,"Se cambio la contraseña correctamente")
            return redirect('manager-dashboard')
        else: # si no es valido vuelve a cargar el formulario y muestar el error
            data = self.make_data()
            data["form"] = form
            data["form_title"]="Actualizar Contraseña"
            data["form_submit_label"] = "Guardar"
            return render(request,"manager/form_as_p_data.html.dtpl",data)