from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import Permission, User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.http import Http404
from django.utils import timezone

from datetime import timedelta
from datetime import datetime,time

from therapist.models import Therapist,GridAvailability,Freeday
from meet.models import Config,Meet,Pay,PayGateway
from patient.models import Patient
from page.models import *


#from stripe import api_key,checkout
import stripe
import pytz
#from zoneinfo import ZoneInfo

#stripe.api_key = 'sk_test_CGGvfNiIPwLXiDwaOfZ3oX6Y'


month_name = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
def get_data_days_from(date,days_after):
        #month_name = ["","Enero","Febrero","Marzo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        weekday_name = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

        data = {}

        days = []
        for i in range(1,4):
            days.append(date + timedelta(days=i))

        for d in days:
            if d.month not in data:
                data[d.month] = {}
                data[d.month]["label"] = "{} {}".format(month_name[d.month],d.year)
                data[d.month]["days"] = {}

        for d in days:
            data[d.month]["days"][d.strftime("%d%m%Y")] = {"label":"{} {}".format(weekday_name[d.weekday()],d.day),
                                            "href":reverse_lazy("qmm-order-step2",args=[d.strftime("%d%m%Y")])}

        return data



class LandingView(View):
    def get(self,request,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title
        data["promo"] = SectionPromo.objects.get(name="promo").text
        data["hero"] = SectionHero.objects.get(name="hero")
        data["ready"] = SectionHero.objects.get(name="ready")



        data["steps"] = steps =  Section.objects.get(name="steps")
        data["step_items"] = steps.step_set.all()

        # steps_items = [steps.step1,steps.step2,steps.step3,steps.step4]
        # data["step_items"] = []

        # step_number = 1
        # for s  in steps_items:
        #     (t,d) = s.split("#")
        #     dd = {}
        #     dd["number"] = step_number
        #     dd["title"] = t
        #     dd["text"] = d
        #     data["step_items"].append(dd)
        #     step_number += 1

        data["advantages"] = adv = Section.objects.get(name="advantages")
        data["ads_items"] = adv.advantage_set.all()
        data["faq"] = faq = Section.objects.get(name="faq")
        data["faq_items"] = faq.frequentquestions_set.all()

        config = Config.objects.get(name="default")
        data["price"] = config.value
        data["duration"] = config.rate
        data["config"] = config

        # ads_items = [adv.adv1,adv.adv2,adv.adv3,adv.adv4]
        # data["step_items"] = []

        # step_number = 1
        # for s  in steps_items:
        #     (t,d) = s.split("#")
        #     dd = {}
        #     dd["number"] = step_number
        #     dd["title"] = t
        #     dd["text"] = d
        #     data["step_items"].append(dd)
        #     step_number += 1
            

        return render(request,"qmm/landing-page.html.dtpl",data)


class NewOrderMeetView(View):
    def get(self,request,**kwargs):
        if "reschedule" in request.session:
            request.session.pop("reschedule")
        return redirect(reverse_lazy("qmm-order-meet"))


class OrderMeetView(View):

    def get(self,request,**kwargs):
        data = {}

        data["title"] = Page.objects.get(name="landing").title+" - "+"Solicitar terapia"
        data["month"] = get_data_days_from(timezone.now(),3)

        config = Config.objects.get(name="default")


        data["resume"] = {"duration":"{} minutos".format(config.rate),
                          "day":"...",
                          "time":"...",
                          "value":"USD {}".format(config.value)}

        print(request.COOKIES)

        
        if "local_timezone" in request.COOKIES:
            request.session["local_timezone"] = request.COOKIES["local_timezone"]
        else:
            request.session["local_timezone"] = "UTC"

        if "selected_timezone" in request.COOKIES:
            request.session["selected_timezone"] = request.COOKIES["selected_timezone"]
        else:
            request.session["selected_timezone"] = request.session["local_timezone"]


        
        data["local_timezone"] = request.session["local_timezone"]        
        data["selected_tz"] = request.session["selected_timezone"]
        data["list_tz"] = pytz.all_timezones

        data["selected"] = 0
        data["selected_meet"] = 0

        return render(request,"qmm/form_order_meet.html.dtpl",data)


class OrderMeetStep2View(View):

    def get(self,request,day,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Solicitar terapia"
        data["month"] = get_data_days_from(timezone.now(),3)
        data["selected"] = day



        day = datetime(int(day[4:8]),int(day[2:4]),int(day[0:2]))

        print(request.COOKIES)
        
        if "selected_timezone" in request.COOKIES:    
            request.session["selected_timezone"] = request.COOKIES["selected_timezone"]

        selected_tz = request.session["selected_timezone"]
        data["local_timezone"] = request.session["local_timezone"]
        patient_tz = selected_tz

        

        dt_patient = pytz.timezone(patient_tz).localize(day)

       

        config = Config.objects.get(name="default")
        labels = config.list_of_meets()

        data["meets"] = {}
        data["selected_tz"] = selected_tz
        data["list_tz"] = pytz.all_timezones
        #meets_aval = {1,2,3}
        #meets_aval = list(meets_aval)
        #meets_aval.sort()


        meets_aval = []
        for t in Therapist.objects.filter(user__is_active=True):
            if not t.freeday_set.filter(date=day.date()).exists():
                meets_aval += t.meet_set.filter(status="F",date__date=dt_patient.strftime("%Y-%m-%d"))

        dicc_aux = {}
        for m in meets_aval:
            label = pytz.timezone(patient_tz).normalize(m.date).strftime("%H:%M")
            dicc_aux[label] = m

        l = list(dicc_aux.keys())
        l.sort()

        for m in l:
           data["meets"][dicc_aux[m].id] = {"label":m,
                                  "href":reverse_lazy("qmm-order-step3",args=[day.strftime("%d%m%Y"),dicc_aux[m].id])}

        #for m in meets_aval:
        #    label = pytz.timezone(patient_tz).normalize(m.date).strftime("%H:%M")
        #    data["meets"][label] = {"label":label,
        #                           "href":reverse_lazy("qmm-order-step3",args=[day.strftime("%d%m%Y"),m.id])}

        data["resume"] = {"duration":"{} minutos".format(config.rate),
                          "day":day.strftime("%d de "+month_name[day.month].lower()+", %Y"),
                          "time":"...",
                          "value":"USD {}".format(config.value)}

        

        data["selected_meet"] = 0

        return render(request,"qmm/form_order_meet.html.dtpl",data)
        

class OrderMeetStep3View(View):

    def get(self,request,day,meet,**kwargs):
        config = Config.objects.get(name="default")

        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Solicitar terapia"
        data["month"] = get_data_days_from(timezone.now(),3)
        data["selected"] = day

        day = datetime(int(day[4:8]),int(day[2:4]),int(day[0:2]))

        meets_aval = set()
        meets_taked = set()
        meets_no_taked = set()

        print(request.COOKIES)
        
        if "selected_timezone" in request.COOKIES:    
            request.session["selected_timezone"] = request.COOKIES["selected_timezone"]

        selected_tz = request.session["selected_timezone"]
        data["local_timezone"] = request.session["local_timezone"]
        patient_tz = selected_tz

        data["meets"] = {}#request.session["meet_aval"]
        data["list_tz"] = pytz.all_timezones
        data["selected_tz"] = selected_tz
       
        
        data["selected_meet"] = int(meet)

        dt_patient = pytz.timezone(patient_tz).localize(day)
        meets_aval = []
        for t in Therapist.objects.filter(user__is_active=True):
            if not t.freeday_set.filter(date=day.date()).exists():
                meets_aval += t.meet_set.filter(status="F",date__date=dt_patient.strftime("%Y-%m-%d"))

        dicc_aux = {}
        for m in meets_aval:
            label = pytz.timezone(patient_tz).normalize(m.date).strftime("%H:%M")
            dicc_aux[label] = m

        l = list(dicc_aux.keys())
        l.sort()

        for m in l:
            data["meets"][dicc_aux[m].id] = {"label":m,
                                   "href":reverse_lazy("qmm-order-step3",args=[day.strftime("%d%m%Y"),dicc_aux[m].id])}




        data["resume"] = {"duration":"{} minutos".format(config.rate),
                          "day":day.strftime("%d de "+month_name[day.month].lower()+", %Y"),
                          "time":data["meets"][int(meet)]["label"],
                          "value":"USD {}".format(config.value)}


        data["step3"] = "step3"



        return render(request,"qmm/form_order_meet.html.dtpl",data)

class CheckoutView(View):

    def get(self,request,day,meet,**kwargs):

        day = datetime(int(day[4:8]),int(day[2:4]),int(day[0:2]))

        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Solicitar terapia"
        config = Config.objects.get(name="default")
        labels = config.list_of_meets()

        meet_object = get_object_or_404(Meet,pk=int(meet))

        patient_tz = request.session["selected_timezone"]

        #tz_u = request.session["tz_u"]
        data["resume"] = {"duration":"{} minutos".format(config.rate),
                          "day":day.strftime("%d de "+month_name[day.month].lower()+", %Y"),
                          "time":pytz.timezone(patient_tz).normalize(meet_object.date).strftime("%H:%M"),
                          "value":"USD {}".format(config.value)}



        data["meet"] = meet
        #data["list_tz"] = pytz.all_timezones

        #elige al terapeuta que va a atender la reunion

        #reprogramacion :O
        if "reschedule" in request.session:
            config = Config.objects.get(name="default")
            to_free_meet = Meet.objects.get(pk=request.session["reschedule"])
            redate_meet = Meet.objects.get(pk=int(meet))

            #asigno la nueva terapia al paciente y le transfiero el pago
            redate_meet.patient = to_free_meet.patient
            pay = to_free_meet.pay_set.all()[0]
            pay.meet = redate_meet
            pay.save()
            redate_meet.value = to_free_meet.value
            redate_meet.status = "R"
            redate_meet.save()
            
            #libero la terapia anterior
            to_free_meet.status="F"
            to_free_meet.patient = None
            to_free_meet.save()

            redate_meet.make_zoom_link()
            to_free_meet.send_email_cancel_therapist()
            redate_meet.send_email_reschedule_patient()
            redate_meet.send_email_therapist()
            #redate_meet.send_emails()

            
            data["title"] = "Cita reprogramada"
            data["description"] = "Tu cita fue reprogramada, en breve te llegará un email con los datos."
            request.session.pop("reschedule")
            return render(request,"qmm/message.html.dtpl",data)

        else:
            config = Config.objects.get(name="default")
            meet_object = Meet.objects.get(pk=int(meet))
            meet_object.value = config.value
            meet_object.status = "T"
            meet_object.created = timezone.now()
            meet_object.save()
            #meet_object = Meet.objects.create(therapist=therapist_meet,timezone=tz_u,number=meet,date=day,status="T",value=config.value,duration=config.rate)
            data["meet_id"] = meet_object.id
            return render(request,"qmm/form_checkout.html.dtpl",data)


class PayView(View):

    def get(self,request,meet,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" "+"Realizando pago"
        data["resume_day"] = "..."
        data["resume_time"] = "..."
        #data["step3"] = "step3"

    def post(self,request,meet,**kwargs):
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email = request.POST["email"]
        telephone = request.POST["country"]+request.POST["telephone"]

        patient_tz = request.session["selected_timezone"]

        try:
            patient = Patient.objects.get(user__email=email)

            patient.timezone_verbose = patient_tz
            patient.save()

        except ObjectDoesNotExist:
            user = User(first_name=firstname,last_name=lastname,email=email,is_active=True)
            user.username = Patient.make_username(user)
            user.save()
            patient = Patient.objects.create(user=user,telephone=telephone,timezone_verbose=patient_tz)
            try:
                patient_group = Group.objects.get(name="patient")
            except:
                patient_group = Group.objects.create(name="patient")
            user.groups.add(patient_group)
            user.save()

            
        meet = get_object_or_404(Meet,pk=meet)
        meet.prepay_step(patient)
        
        gateway = PayGateway.objects.get(name="paypal")

        try:
            pay = Pay.objects.get(meet=meet)
        except ObjectDoesNotExist:
            pay = Pay.objects.create(meet=meet,amount=meet.value,status="P",gateway=gateway)
        
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Realizando pago"
        data["meet_id"] = meet.id
        data["meet"] = meet
        data["gateway"] = gateway
        data["pay"] = pay

        return render(request,"qmm/pay.html.dtpl",data)

class PayCheckoutStripeView(View):

    def get(self,request,meet,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" "+"Realizando pago"
        data["resume_day"] = "..."
        data["resume_time"] = "..."
        #data["step3"] = "step3"

    def post(self,request,pay_id,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" "+"Realizando pago"
        data["resume_day"] = "..."
        data["resume_time"] = "..."

        config = Config.objects.get(name="default")

        server = config.server

        gateway = PayGateway.objects.get(name="stripe")
        stripe.api_key = gateway.token #'sk_test_CGGvfNiIPwLXiDwaOfZ3oX6Y'

        pay = get_object_or_404(Pay,pk=pay_id)
        pay.gateway = gateway
        pay.save()


        try:
            product = stripe.Product.create(name="Terapia")

            price = stripe.Price.create(
                              product=product.id,
                              unit_amount=int(pay.amount*100),
                              currency=gateway.currency,
                            )

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': price.id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=server+reverse_lazy('qmm-pay-confirm',args=[pay_id]),
                cancel_url=server+reverse_lazy('qmm-pay-cancel',args=[pay_id]),
            )
        except Exception as e:
            data = {}
            data["error_description"] = str(e) + " " + reverse_lazy('qmm-pay-confirm',args=[pay_id])
            return render(request,"qmm/pay_cancel.html.dtpl",data)
        pay.transaction_code = checkout_session.id
        pay.save()

        return redirect(checkout_session.url, code=303)

        #return render(request,"qmm/pay.html.dtpl",data)



class PayConfirmView(View):

    def get(self,request,pay,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Confirmación del pago"
        pay = get_object_or_404(Pay,pk=pay)


        #if pay.status != "D":
        if "idt" in request.GET:
            pay.transaction_code = request.GET["idt"]
        
        if pay.status == "P":
            pay.confirm()
            pay.meet.confirm()
            pay.meet.make_zoom_link()
            pay.meet.send_emails()
            return render(request,"qmm/pay_confirm.html.dtpl",data)
        else:
            return redirect(reverse_lazy("qmm-landing"))

class PayCancelView(View):

    def get(self,request,pay,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Pago no aprobado"
        pay = get_object_or_404(Pay,pk=pay)


        #if pay.status != "D":
        return render(request,"qmm/pay_confirm.html.dtpl",data)



class MeetCancelView(View):

    def get(self,request,meet,**kwargs):
        data = {}
        meet = get_object_or_404(Meet,pk=meet)
        if meet.status in ["D","R"]:
            meet.cancel()
            meet.send_emails()
            Meet.objects.create(therapist=meet.therapist,status="F",date=meet.date,duration=meet.duration)

            return render(request,"qmm/meet_cancel.html.dtpl",data)
        else:
            data["title"] = "Cita cancelada"
            data["description"] = "La cita se encuentra cancelada"
            return render(request,"qmm/message.html.dtpl",data)

class MeetCancelTherapistView(View):

    def get(self,request,meet,**kwargs):
        data = {}
        meet = get_object_or_404(Meet,pk=meet)
        if meet.status in ["D","R"]:

            meets_same_date_free = Meet.objects.filter(date=meet.date,status="F")

            
            if len(meets_same_date_free) == 0:
                meet.cancel()
                meet.send_emails()
            else: #si hay otra cita libre con la misma fecha y hora se lo asigna

                #si se reasigna reterapeuta, envio mail cancelacion al viejo y al paciente no le cambia nada.
                meet.send_email_cancel_therapist()
                meet.cancel()
                #meet.therapist = therapist_meet
                meet.save()
                #meet.send_email_therapist()
                new_meet = meets_same_date_free[0]
                new_meet.patient = meet.patient
                new_meet.confirm()
                new_meet.send_email_therapist()
                

            return render(request,"qmm/meet_cancel.html.dtpl",data)
        else:
            data["title"] = "Cita cancelada"
            data["description"] = "La cita se encuentra cancelada"
            return render(request,"qmm/message.html.dtpl",data)

class MeetRedateView(View):

    def get(self,request,meet,**kwargs):
        data = {}
        meet = get_object_or_404(Meet,pk=meet)
        if meet.status in ["D","R"]:
            request.session["reschedule"] = meet.id
            return redirect(reverse_lazy("qmm-order-meet"))
            #return render(request,"qmm/meet_reschedule.html.dtpl",data)
        else:
            data["title"] = "Cita cancelada"
            data["description"] = "La cita se encuentra cancelada"
            return render(request,"qmm/message.html.dtpl",data)



class TherapistView(LoginRequiredMixin,View):
    login_url = reverse_lazy("qmm-login")


    def get(self,request,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Terapereuta"

        if not Therapist.objects.filter(user=request.user).exists():
            return render(request,"qmm/no_therapist.html.dtpl",data)


        therapist = Therapist.objects.get(user=self.request.user)

        data["therapist"] = therapist
        #data["meets"] = therapist.meet_set.filter(date__gte=timezone.now())
        data["meets"] = therapist.meet_set.all()


        data["month"] = get_data_days_from(timezone.now(),3)

        data["days"] = {}


        total_days = 7
        meets_in_day = timezone.now()
        for i in range(0,total_days):
            
            ms = therapist.meet_set.filter(date=meets_in_day.date(),status="D",date__gte=timezone.now().date()).order_by("number")


            days_data = {"date":meets_in_day.strftime("%Y-%m-%d"),
                            "meets":ms,
                            "lock":therapist.freeday_set.filter(date=meets_in_day.date()).exists()}


            if i == 0:
                data["days"]["Hoy"] = days_data
            else:
                data["days"][meets_in_day.strftime("%d/%m")] = days_data
            meets_in_day+=timedelta(days=1)


            #"27/4","28/4","29,4"]#get_data_days_from(timezone.now(),3)
            
        data["selected"] = 0
        data["selected_meet"] = 0

        return render(request,"qmm/therapist.html.dtpl",data)


class TherapistAvailabilityView(LoginRequiredMixin,View):
    login_url = reverse_lazy("qmm-login")


    def get(self,request,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Terapereuta"

        if not Therapist.objects.filter(user=request.user).exists():
            return render(request,"qmm/no_therapist.html.dtpl",data)


        therapist = Therapist.objects.get(user=self.request.user)

        data["therapist"] = therapist
        #data["meets"] = therapist.meet_set.filter(date__gte=timezone.now())
        #data["meets"] = therapist.meet_set.all()


        data["month"] = get_data_days_from(timezone.now(),3)

        data["days"] = {}


        total_days = 7
        meets_in_day = timezone.now()
        days_names = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sabado","Domingo" ]

        config = Config.objects.get(name="default")

        labels = []
        values = []
        for i in range(0,config.max_number()):
            init_time = datetime(month=1,day=1,year=1990)
            meet_begin = init_time + config.make_meet_begin(i)
            meet_end = init_time + config.make_meet_end(i)
            str_f_time = "%H:%M"
            labels.append("{}-{}".format(meet_begin.strftime(str_f_time),meet_end.strftime(str_f_time)))

        days = []
        for i in range(0,total_days):
            schedule = []

            for m in therapist.availability(i):
                schedule.append(labels[m])


            days.append({"name":days_names[i],
                         "schedule":schedule,
                         "labels":labels})
            #data["days"][days_names[i]] = self.labels #{"schedule":days_names[i]}
        data["days"] = days;
        data["selected"] = 0
        data["selected_meet"] = 0

        return render(request,"qmm/therapist_availability.html.dtpl",data)

    def post(self,request):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Terapereuta"

        if not Therapist.objects.filter(user=request.user).exists():
            return render(request,"qmm/no_therapist.html.dtpl",data)

        therapist = Therapist.objects.get(user=self.request.user)

        days_names = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sabado","Domingo"]

        config = Config.objects.get(name="default")

        labels = []
        values = []
        for i in range(0,config.max_number()):
            init_time = datetime(month=1,day=1,year=1990)
            meet_begin = init_time + config.make_meet_begin(i)
            meet_end = init_time + config.make_meet_end(i)
            str_f_time = "%H:%M"
            labels.append("{}-{}".format(meet_begin.strftime(str_f_time),meet_end.strftime(str_f_time)))

        try:
            g = GridAvailability.objects.get(therapist=therapist)
        except:
            g = GridAvailability.objects.create(therapist=therapist)

        g.rate = config.rate + config.interval

        print(request.POST)
        for d in range(0,7):
            if days_names[d] in request.POST:
                print("Guarda"+days_names[d])
                availability = []
                for i in range(0,config.max_number()):
                    if labels[i]+days_names[d] in request.POST:
                        availability.append(str(i))
                print(availability)
                print(g.get_day_for_number(d))
                g.set_day_for_number(d,GridAvailability.list_to_str(availability,config.max_number()))
                print(g.get_day_for_number(d))
        g.save()

        return redirect('qmm-therapist-availability')


class TherapistLockDayView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,day,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Terapereuta"

        if not Therapist.objects.filter(user=request.user).exists():
            return render(request,"qmm/no_therapist.html.dtpl",data)

        therapist = Therapist.objects.get(user=self.request.user)
        fd = Freeday(therapist=therapist,date=day)
        fd.save()
        #therapist.freeday_set().create(date=day)

        return redirect('qmm-therapist')

class TherapistUnlockDayView(LoginRequiredMixin,View):
    login_url = reverse_lazy("manager-login")
    #redirect_field_name = 'redirect_to'
    def get(self,request,day,**kwargs):
        data = {}
        data["title"] = Page.objects.get(name="landing").title+" - "+"Terapereuta"

        if not Therapist.objects.filter(user=request.user).exists():
            return render(request,"qmm/no_therapist.html.dtpl",data)

        therapist = Therapist.objects.get(user=self.request.user)
        therapist.freeday_set.filter(date=day).delete()

        return redirect('qmm-therapist')

class LoginView(View):
    def get(self,request,**kwargs):
        page = {}
        #login = LoginPage.objects.get(name="root")
        page["title"] = Page.objects.get(name="landing").title+" - "+"Login"
        
        #login["title"] = "N3SYSTEM"
        return render(request,"qmm/login.html.dtpl",{"page":page})

    def post(self,request,**kargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and Therapist.objects.filter(user=user).exists():
            login(self.request,user)
            if 'next' in self.request.GET:
                return redirect(self.request.GET['next'])

            return redirect('qmm-therapist')

        else:
            messages.error(self.request, 'Usuario o contraseña incorrecto')
            return redirect('qmm-login')


class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect("qmm-login")



