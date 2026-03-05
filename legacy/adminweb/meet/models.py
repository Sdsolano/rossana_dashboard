from django.db import models
from datetime import timedelta
from django.utils import timezone
# Create your models here.

from patient.models import Patient
#from therapist.models import Therapist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.urls import reverse_lazy

from base64 import b64encode
import json

import requests
import pytz

class Meet(models.Model):
    STATUS=(
        ('F',"Libre"),
        ('T',"Temporal"),
        ('U',"Pago Pediente"),
        ('D',"Confirmado"),
        ('R',"Reprogramado"),
        ('C',"Cancelado"),
        ('P',"Presente"),
        ('A',"Ausente"),
    )

    patient = models.ForeignKey(Patient,on_delete=models.CASCADE,null=True)
    therapist = models.ForeignKey("therapist.Therapist",on_delete=models.CASCADE)
    date = models.DateTimeField(null=True,default=None)

    duration = models.IntegerField(null=True,default=None)
    timezone = models.IntegerField(null=True,default=0)
    number = models.IntegerField(null=True,default=None)
    value = models.DecimalField(default=0,null=False,max_digits=10,decimal_places=2)
    cache_begin = models.DateTimeField(null=True,default=None)
    cache_end = models.DateTimeField(null=True,default=None)

    created = models.DateTimeField(auto_now_add=True,null=False)
    status = models.CharField(max_length=1,choices=STATUS)

    ct_email_patient_send = models.IntegerField(null=False,default=0)
    ct_email_therapist_send = models.IntegerField(null=False,default=0)

    ct_email_patient_remember = models.IntegerField(null=False,default=0)
    ct_email_therapist_remember = models.IntegerField(null=False,default=0)

    ct_email_patient_quality_survey = models.IntegerField(null=False,default=0)
    ct_email_therapist_quality_survey = models.IntegerField(null=False,default=0)


    def __str__(self):
        return self.code()

    def update_cache(self):
        pass
        #config = Config.objects.get(name="default")
        #self.cache_begin = self.date + config.make_meet_begin(self.number)
        #self.cache_end = self.date + config.make_meet_end(self.number)

    def begin(self):
        config = Config.objects.get(name="default")
        return config.make_meet_begin(self.number)

    def date_begin(self):
        return self.date

    def date_patient_24hs(self):
        return pytz.timezone(self.patient.timezone_verbose).normalize(self.date).strftime("%d-%m-%Y %H:%M")

    def date_patient_ampm(self):
        return pytz.timezone(self.patient.timezone_verbose).normalize(self.date).strftime("%d-%m-%Y %I:%M%p")


    def date_begin_th(self):
        
        return self.date

    def date_therapist_24hs(self):
        return pytz.timezone(self.therapist.timezone_verbose).normalize(self.date).strftime("%d-%m-%Y %H:%M")


    def date_therapist_ampm(self):
        return pytz.timezone(self.therapist.timezone_verbose).normalize(self.date).strftime("%d-%m-%Y %I:%M%p")



    def end(self):
        config = Config.objects.get(name="default")
        return config.make_meet_end(self.number)

    def code(self):
        init_number = 1000
        return "QCT{:09}".format(self.id+init_number)


    def print_tz(self):
        
        
        signo= "-" if self.timezone < 0 else "+"
        
        return "UTC{}{}:00".format(signo,abs(int(self.timezone/60)))

    def prepay_step(self,patient):
        self.patient=patient
        self.status="U"
        self.save()

    def email_signature(self,config):
        return f"Escuela QMM\n{config.support}"

    def send_email_patient_remember(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]


        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/patient_remember.html.dtpl",{
                        "firstname":self.patient.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.patient.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_patient_remember+=1
            self.save()
        return result

    def send_email_patient_survey(self):
        config = Config.objects.get(name="default")
        server = config.server

        

        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/patient_survey.html.dtpl",{
                        "firstname":self.patient.user.first_name,
                        "meet":self,
                        "config":config,
                        "survey_link":"https://esbdigital.typeform.com/to/sQnsoZ4R",
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.patient.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_patient_quality_survey+=1
            self.save()
        return result

    def send_email_patient(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]


        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/patient.html.dtpl",{
                        "firstname":self.patient.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.patient.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_patient_send+=1
            self.save()
        return result

    def send_email_reschedule_patient(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]


        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/reschedule_patient.html.dtpl",{
                        "firstname":self.patient.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.patient.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_patient_send+=1
            self.save()
        return result

    def send_email_cancel_patient(self):
        config = Config.objects.get(name="default")
        server = config.server

        result = send_mail("Cancelacion de cita de QMM",
                    render_to_string("mails/cancel_patient.html.dtpl",{
                        "firstname":self.patient.user.first_name,
                        "meet":self,
                        "config":config,
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.patient.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_patient_send+=1
            self.save()
        return result

    def send_email_therapist_remember(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]

        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/therapist_remember.html.dtpl",{
                        "firstname":self.therapist.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.therapist.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_therapist_send+=1
            self.save()
        return result

    def send_email_therapist_remember(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]

        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/therapist_remember.html.dtpl",{
                        "firstname":self.therapist.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.therapist.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_therapist_send+=1
            self.save()
        return result


    def send_email_therapist(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]

        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/therapist.html.dtpl",{
                        "firstname":self.therapist.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.therapist.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_therapist_send+=1
            self.save()
        return result

    def send_email_reschedule_therapist(self):
        config = Config.objects.get(name="default")
        server = config.server

        zm = self.zoommeet_set.all()

        if len(zm) == 0:
            self.make_zoom_link()

        zoom_meet = zm[0]

        result = send_mail("Sistema QMM Team",
                    render_to_string("mails/reschedule_therapist.html.dtpl",{
                        "firstname":self.therapist.user.first_name,
                        "meet":self,
                        "config":config,
                        "zoom_link":zoom_meet.link,
                        "zoom_pass":zoom_meet.password,
                        "cancel_link":server+reverse_lazy("qmm-meet-cancel",args=[self.id]),
                        "redate_link":server+reverse_lazy("qmm-meet-redate",args=[self.id]),
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.therapist.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_therapist_send+=1
            self.save()
        return result

    def send_email_cancel_therapist(self):
        config = Config.objects.get(name="default")
        server = config.server

        result = send_mail("Cancelacion de cita de QMM",
                    render_to_string("mails/cancel_therapist.html.dtpl",{
                        "firstname":self.therapist.user.first_name,
                        "meet":self,
                        "config":config,
                        "signature":self.email_signature(config)}),
                    "Equipo QMM <germancuacci@indag.net>",
                    [self.therapist.user.email],
                    fail_silently=False
                )

        if result:
            self.ct_email_patient_send+=1
            self.save()
        return result

    def make_zoom_link(self):
        self.zoommeet_set.all().delete()
        
        zm = ZoomMeet()
        zm.meet = self
        zm.create_meeting(f"Sistema QMM Team - {self.code()}")


    def confirm(self):
        self.status = "D"
        self.save()
        #self.make_zoom_link()

    def cancel(self):
        self.status = "C"
        self.save()
        #self.make_zoom_link()        

    def send_emails(self):
        r = 0
        if self.status == "D":
            r &= self.send_email_patient()
            r &= self.send_email_therapist()

        if self.status == "C":
            r &= self.send_email_cancel_patient()
            r &= self.send_email_cancel_therapist()

        if self.status == "R":
            r &= self.send_email_reschedule_patient()
            r &= self.send_email_reschedule_therapist()

        return r

    def task_send_email_remember(self):
        if self.status == "D":
            if (self.date - timedelta(minutes=60)) < timezone.now():
                if self.ct_email_patient_remember == 0:
                    self.send_email_patient_remember()
                    self.send_email_therapist_remember()

    def task_send_email_survey(self):
        if self.status == "D":
            if (self.date + timedelta(minutes=45)) < timezone.now(): 
                if self.ct_email_patient_quality_survey == 0:
                    self.send_email_patient_survey()
                
    def zoom(self):
        zm = self.zoommeet_set.all()
        if len(zm) == 0:
            return None

        return zm[0]


    @staticmethod
    def remove_temporals():
        config = Config.objects.get(name="default")
        Meet.objects.filter(status="T",created__lt=timezone.now()-timezone.timedelta(minutes=config.temporal_timeout)).delete()

class ZoomMeet(models.Model):
    meet = models.ForeignKey(Meet,on_delete=models.CASCADE)
    zoom_id = models.BigIntegerField(null=True)
    link = models.CharField(max_length=1000,null=True)
    password = models.CharField(max_length=1000,null=True)

    def create_meeting(self,topic):
        zoom = Zoom.objects.get(name="default")
        (self.zoom_id,self.link,self.password) = zoom.create_meeting(self.meet.date,self.meet.duration,topic)
        self.save()


class Zoom(models.Model):
    name = models.CharField(max_length=1000,default="default",null=True)
    account_id = models.CharField(max_length=1000,null=True)
    client_id = models.CharField(max_length=1000,null=True)
    client_secret = models.CharField(max_length=1000,null=True)

    def base64_auth(self):
        return b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")).decode("utf-8")

    def get_token(self):
        #Ejemplo en curl: curl -X POST https://zoom.us/oauth/token -d 'grant_type=account_credentials' -d 'account_id={accountID}' -H 'Host: zoom.us' -H 'Authorization: Basic Base64Encoded(clientId:clientSecret)'
        h = {'host':'zoom.us',
            'authorization': f'Basic {self.base64_auth()}'}
        d={'grant_type':'account_credentials',
            'account_id':self.account_id}
        r = requests.post("https://zoom.us/oauth/token",headers=h,data=d)
        #podria checkear los permios necesario, y avisar de no tenerlos ¡! :O
        print(f"Status code {r.status_code}")
        return json.loads(r.text)["access_token"]

    def create_meeting(self,date,duration,topic):
        meetingdetails = {"topic": topic,
                  "type": 2,
                  "start_time": date.strftime("%Y-%m-%dT%H: %M: %S"),#"2023-03-16T10: 00: 57",
                  "duration": duration,
                  "timezone": "UTC",#"America/Argentina/Buenos_Aires",
                  "agenda": "Agendado por sistema QMM",
 
                  "recurrence": {"type": 1,
                                 "repeat_interval": 1
                                 },
                  "settings": {"host_video": "true",
                               "participant_video": "true",
                               "join_before_host": "False",
                               "mute_upon_entry": "False",
                               "watermark": "true",
                               "audio": "voip",
                               "auto_recording": "cloud"
                               }
                  }

        #hay que pedir el token cada vez que se crea una reunion?
        headers = {'authorization': f'Bearer {self.get_token()}',
                   'content-type': 'application/json'}

        #aca hay que pasarle el usuario en lugar de "me" si no es el usuario admin
        r = requests.post(f'https://api.zoom.us/v2/users/me/meetings',headers=headers, data=json.dumps(meetingdetails))
        print(date)
        print(date.strftime("%Y-%m-%dT%H: %M: %S"))

        if r.status_code == 201:
            d = json.loads(r.text)
            return (d["id"],d["join_url"],d["password"])
        else:
            return (None,None)



class Config(models.Model):
    name = models.CharField(max_length=100)
    rate = models.IntegerField(default=40) #rate in minutes
    value = models.DecimalField(default=200.00,null=False,max_digits=10,decimal_places=2)
    server = models.CharField(max_length=200,null=True)
    support = models.CharField(max_length=1000,null=True)
    support_wa = models.CharField(max_length=1000,null=True)
    temporal_timeout = models.IntegerField(default=5) #timeout in minutes
    interval = models.IntegerField(default=5) #interval in minutes

    def max_number(self):
        minutes_of_a_day = 24*60
        return int(minutes_of_a_day/(self.rate+self.interval))

    def make_meet_begin(self,number):
        return timedelta(minutes=number*(self.rate+self.interval))

    def make_meet_end(self,number):
        if timedelta(minutes=(number+1)*(self.rate+self.interval)) < timedelta(days=1):
            return timedelta(minutes=(number+1)*(self.rate+self.interval))
        else:
            return timedelta(minutes=(number+1)*(self.rate+self.interval)) - timedelta(days=1)
        
    def list_of_meets(self):
        ret = []
        for i in range(0,self.max_number()):
            ret.append((int(i),"{}".format(str(self.make_meet_begin(i))[:-3],str(self.make_meet_end(i))[:-3])))
        return ret


class Pay(models.Model):
    STATUS=(
        ('P',"Pediente"),
        ('D',"Hecho"),
        ('C',"Cancelado"),
        ('R',"Reembolsado"),
    )

    meet = models.ForeignKey(Meet,on_delete=models.SET_NULL,null=True)
    gateway = models.ForeignKey('PayGateway',on_delete=models.SET_NULL,null=True)
    amount = models.DecimalField(default=0,null=False,max_digits=10,decimal_places=2)
    transaction_code = models.CharField(max_length=1000)
    status = models.CharField(max_length=1,choices=STATUS)
    timestamp = models.DateTimeField(auto_now_add=True,null=False)

    def __str__(self):
        return self.code()

    def code(self):
        init_number = 1000
        return "QP{:09}".format(self.id+init_number)

    def confirm(self):
        self.status = "D"
        self.save()

    

class PayGateway(models.Model):
    name = models.CharField(max_length=200,primary_key=True)
    token = models.CharField(max_length=1000)
    currency = models.CharField(max_length=10,default="USD")
    timestamp = models.DateTimeField(auto_now_add=True,null=False)
    def __str__(self):
        return self.name



