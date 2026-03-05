from django.utils.translation import gettext_lazy as _
from django.forms import *
from meet.models import Config



class ConfigForm(Form):

    
    rate = CharField(label=_('Duracion de la cita (minutos)'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    interval = CharField(label=_('Intervalo entre citas (minutos)'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    value = CharField(label=_('Valor de la cita (USD):'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    server = CharField(label=_('Nombre del servidor'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    support = CharField(label=_('Email de Soporte'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    support_wa = CharField(label=_('Soporte por Whatsapp'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    temporal_timeout = CharField(label=_('Tiempo de reserva temporal de la cita (minutos)'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))


    #zoom_account_id = CharField(label=_('Zoom - Account id'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    #zoom_client_id = CharField(label=_('Zoom - Client id'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    #zoom_client_secret = CharField(label=_('Zoom - Client secret'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def save(self):
        config = Config.objects.get(name="default")

        config.rate = self.cleaned_data["rate"]
        config.interval = self.cleaned_data["interval"]
        config.value = self.cleaned_data["value"]
        config.server = self.cleaned_data["server"]
        config.temporal_timeout = self.cleaned_data["temporal_timeout"]
        config.support = self.cleaned_data["support"]
        config.support_wa = self.cleaned_data["support_wa"]

        config.save()
        

    def load(self):
        config = Config.objects.get(name="default")
        
        self.fields["rate"].initial = config.rate
        self.fields["interval"].initial = config.interval
        self.fields["value"].initial = config.value
        self.fields["server"].initial = config.server
        self.fields["temporal_timeout"].initial = config.temporal_timeout
        self.fields["support"].initial = config.support
        self.fields["support_wa"].initial = config.support_wa
        
        
        
class UserPasswordForm(Form):
    password = CharField(label=_('Contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = CharField(label=_('Repetir contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
        #active = BooleanField(label="",initial=False,required=False,widget=PaperCheckboxInput(attrs={'label':_("Activo")}))

    def clean_password_confirm(self):
        password = self.cleaned_data['password']
        if password != self.cleaned_data['password_confirm']:
            raise ValidationError('No coinciden las contraseñas')
        return password

    def save(self,u):
        if self.cleaned_data["password"]:
            u.set_password(self.cleaned_data["password"])
        u.save()



