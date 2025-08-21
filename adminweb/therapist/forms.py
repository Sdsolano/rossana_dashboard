from django.forms import *
from django.utils.translation import gettext_lazy as _

from meet.models import Config

from .models import *

import pytz

class TherapistAddForm(Form):
    HORARIOS=[]

    TIMEZONES = []

    username = CharField(label=_('Usuario'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    firstname = CharField(label=_('Nombre'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    lastname = CharField(label=_('Apellido'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(label=_('email'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(label=_('Contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = CharField(label=_('Repetir contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))

    #timzone = ChoiceField(label=_("Zona horaria"),widget=RadioSelect(attrs={'class': 'form-control'}), choices=CHOICES)

    timezone = ChoiceField(label=_("Zona horaria"),choices=[],widget=Select(attrs={'class': 'form-control'}))


    monday = MultipleChoiceField(label=_('Lunes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    tuesday = MultipleChoiceField(label=_('Martes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    wednesday = MultipleChoiceField(label=_('Miercoles'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    thursday = MultipleChoiceField(label=_('Jueves'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    friday = MultipleChoiceField(label=_('Viernes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    saturday = MultipleChoiceField(label=_('Sabado'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    sunday = MultipleChoiceField(label=_('Domingo'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    #test = MultipleChoiceField(widget=CheckboxSelectMultiple,choices=HORARIOS)

    active = BooleanField(label=_('Activo'),required=False)
        #active = BooleanField(label="",initial=False,required=False,widget=PaperCheckboxInput(attrs={'label':_("Activo")}))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = Config.objects.get(name="default")

        self.HORARIOS = []
        values = []
        for i in range(0,config.max_number()):
            self.HORARIOS.append((int(i),"{} a {}".format(config.make_meet_begin(i),config.make_meet_end(i))))

        list_of_timezones = ["UTC{}:00".format(i) for i in range(-12,0)] +  ["UTC+{}:00".format(i) for i in range(0,12)]
        self.TIMEZONES = [(i,list_of_timezones[i]) for i in range(0,len(list_of_timezones))]
        

        self.fields["timezone"].choices = self.TIMEZONES


        self.fields["monday"].choices = self.HORARIOS
        self.fields["tuesday"].choices = self.HORARIOS
        self.fields["wednesday"].choices = self.HORARIOS
        self.fields["thursday"].choices = self.HORARIOS
        self.fields["friday"].choices = self.HORARIOS
        self.fields["saturday"].choices = self.HORARIOS
        self.fields["sunday"].choices = self.HORARIOS
       
        #self.fields["monday"].initial = [0,1,3,4,20]

    def clean_password_confirm(self):
        password = self.cleaned_data['password']
        if password != self.cleaned_data['password_confirm']:
            raise ValidationError('No coinciden las contraseñas')
        return password

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('El usuario ya existe. Elija otro nombre.')
        return username

    def save(self):
        u = User.objects.create(username=self.cleaned_data["username"])
        t = Therapist.objects.create(user=u)
        
        u.first_name = self.cleaned_data["firstname"]
        u.last_name = self.cleaned_data["lastname"]
        u.email = self.cleaned_data["email"]
        u.is_active = self.cleaned_data["active"]
        if self.cleaned_data["password"]:
            u.set_password(self.cleaned_data["password"])

        try:
            therapist_group = Group.objects.get(name="therapist")
        except:
            therapist_group = Group.objects.create(name="therapist")

        u.groups.add(therapist_group)
        u.save()

        config = Config.objects.get(name="default")

        g = GridAvailability.objects.create(therapist=t)
        g.timezone = range(-12,12)[self.cleaned_data["timezone"]]*60
        g.rate = config.rate + config.interval
        g.monday = GridAvailability.list_to_str(self.cleaned_data["monday"],config.max_number())
        g.tuesday = GridAvailability.list_to_str(self.cleaned_data["tuesday"],config.max_number())
        g.wednesday = GridAvailability.list_to_str(self.cleaned_data["wednesday"],config.max_number())
        g.thursday = GridAvailability.list_to_str(self.cleaned_data["thursday"],config.max_number())
        g.friday = GridAvailability.list_to_str(self.cleaned_data["friday"],config.max_number())
        g.saturday = GridAvailability.list_to_str(self.cleaned_data["saturday"],config.max_number())
        g.sunday = GridAvailability.list_to_str(self.cleaned_data["sunday"],config.max_number())
        g.save()

        t.rangear()


    def load(self,therapist):
        self.fields["username"].initial = therapist.user.username
        self.fields["firstname"].initial = therapist.user.first_name
        self.fields["lastname"].initial = therapist.user.last_name
        self.fields["email"].initial = therapist.user.email
        self.fields["active"].initial = therapist.user.is_active
        #self.fields["active"].initial = sheet.active
        #self.fields["categorie"].initial = sheet.categorie()


class TherapistEditForm(Form):
    HORARIOS=[]

    TIMEZONES = [] #{(1,"UTC"), (2, "UTC+1:00")}

    username = CharField(label=_('Usuario'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    firstname = CharField(label=_('Nombre'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    lastname = CharField(label=_('Apellido'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(label=_('email'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))

    timezone = ChoiceField(label=_("Zona horaria"),choices=[],widget=Select(attrs={'class': 'form-control'}))


    monday = MultipleChoiceField(label=_('Lunes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    tuesday = MultipleChoiceField(label=_('Martes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    wednesday = MultipleChoiceField(label=_('Miercoles'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    thursday = MultipleChoiceField(label=_('Jueves'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    friday = MultipleChoiceField(label=_('Viernes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    saturday = MultipleChoiceField(label=_('Sabado'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    sunday = MultipleChoiceField(label=_('Domingo'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}),required=False)
    
    active = BooleanField(label=_('Activo'),required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = Config.objects.get(name="default")

        self.HORARIOS = []
        values = []
        for i in range(0,config.max_number()):
            self.HORARIOS.append((i,"{} a {}".format(config.make_meet_begin(i),config.make_meet_end(i))))

        list_of_timezones = pytz.all_timezones#["UTC{}:00".format(i) for i in range(-12,0)] +  ["UTC+{}:00".format(i) for i in range(0,12)]
        self.TIMEZONES = [(list_of_timezones[i],list_of_timezones[i]) for i in range(0,len(list_of_timezones))]


        self.fields["timezone"].choices = self.TIMEZONES

        self.fields["monday"].choices = self.HORARIOS
        self.fields["tuesday"].choices = self.HORARIOS
        self.fields["wednesday"].choices = self.HORARIOS
        self.fields["thursday"].choices = self.HORARIOS
        self.fields["friday"].choices = self.HORARIOS
        self.fields["saturday"].choices = self.HORARIOS
        self.fields["sunday"].choices = self.HORARIOS

    #def clean_username(self):
    #    username = self.cleaned_data['username']
    #    if User.objects.filter(username=username).exists():
    #        raise ValidationError('El usuario ya existe. Elija otro nombre.')
    #    return username

        #active = BooleanField(label="",initial=False,required=False,widget=PaperCheckboxInput(attrs={'label':_("Activo")}))

    def clean_monday(self):
        monday = self.cleaned_data["monday"]
        
        return monday        

    def save(self,therapist):
        u = therapist.user
        u.username = self.cleaned_data["username"]
        u.first_name = self.cleaned_data["firstname"]
        u.last_name = self.cleaned_data["lastname"]
        u.email = self.cleaned_data["email"]
        u.is_active = self.cleaned_data["active"]
        u.save()


        config = Config.objects.get(name="default")


        #g = GridAvailability.objects.get(therapist=therapist)

        try:
            g = GridAvailability.objects.get(therapist=therapist)
        except:
            g = GridAvailability.objects.create(therapist=therapist)

        g.rate = config.rate + config.interval

        g.timezone = 0#(int(self.cleaned_data["timezone"])-12)*60
        g.monday = GridAvailability.list_to_str(self.cleaned_data["monday"],config.max_number())
        g.tuesday = GridAvailability.list_to_str(self.cleaned_data["tuesday"],config.max_number())
        g.wednesday = GridAvailability.list_to_str(self.cleaned_data["wednesday"],config.max_number())
        g.thursday = GridAvailability.list_to_str(self.cleaned_data["thursday"],config.max_number())
        g.friday = GridAvailability.list_to_str(self.cleaned_data["friday"],config.max_number())
        g.saturday = GridAvailability.list_to_str(self.cleaned_data["saturday"],config.max_number())
        g.sunday = GridAvailability.list_to_str(self.cleaned_data["sunday"],config.max_number())
        g.save()

        therapist.timezone_verbose = self.cleaned_data["timezone"]
        therapist.save()
        therapist.rangear()
    

    def load(self,therapist):
        self.fields["username"].initial = therapist.user.username
        self.fields["firstname"].initial = therapist.user.first_name
        self.fields["lastname"].initial = therapist.user.last_name
        self.fields["email"].initial = therapist.user.email
        self.fields["active"].initial = therapist.user.is_active
        self.fields["timezone"].initial = therapist.timezone_verbose

        try:
            grid = GridAvailability.objects.get(therapist=therapist)
           # self.fields["timezone"].initial = int(grid.timezone/60) + 12
            self.fields["monday"].initial = GridAvailability.str_to_list(grid.monday)
            self.fields["tuesday"].initial = GridAvailability.str_to_list(grid.tuesday)
            self.fields["wednesday"].initial = GridAvailability.str_to_list(grid.wednesday)
            self.fields["thursday"].initial = GridAvailability.str_to_list(grid.thursday)
            self.fields["friday"].initial = GridAvailability.str_to_list(grid.friday)
            self.fields["saturday"].initial = GridAvailability.str_to_list(grid.saturday)
            self.fields["sunday"].initial = GridAvailability.str_to_list(grid.sunday)
        except:
            pass

        #config = Config.objects.get(name="default")

class TherapistPasswordForm(Form):
    password = CharField(label=_('Contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = CharField(label=_('Repetir contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
        #active = BooleanField(label="",initial=False,required=False,widget=PaperCheckboxInput(attrs={'label':_("Activo")}))

    def clean_password_confirm(self):
        password = self.cleaned_data['password']
        if password != self.cleaned_data['password_confirm']:
            raise ValidationError('No coinciden las contraseñas')
        return password

    def save(self,c):
        u = c.user
        if self.cleaned_data["password"]:
            u.set_password(self.cleaned_data["password"])
        u.save()



class TherapistAvailibleForm(Form):
    HORARIOS=[]

    therapist = ModelChoiceField(label=_('Terapeuta'),queryset=None,widget=Select(attrs={'class': 'form-control'}))
    
    monday = MultipleChoiceField(label=_('Lunes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))
    tuesday = MultipleChoiceField(label=_('Martes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))
    wednesday = MultipleChoiceField(label=_('Miercoles'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))
    thursday = MultipleChoiceField(label=_('Jueves'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))
    friday = MultipleChoiceField(label=_('Viernes'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))
    saturday = MultipleChoiceField(label=_('Sabado'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))
    sunday = MultipleChoiceField(label=_('Domingo'),choices=HORARIOS,widget=SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = Config.objects.get(name="default")

        self.HORARIOS = []
        for i in range(0,config.max_number()):
            self.HORARIOS.append((i,"{} a {}".format(config.make_meet_begin(i),config.make_meet_end(i))))

        self.fields["monday"].choices = self.HORARIOS
        self.fields["thursday"].choices = self.HORARIOS
        self.fields["wednesday"].choices = self.HORARIOS
        self.fields["thursday"].choices = self.HORARIOS
        self.fields["friday"].choices = self.HORARIOS
        self.fields["saturday"].choices = self.HORARIOS
        self.fields["sunday"].choices = self.HORARIOS

        self.fields['therapist'].queryset = Therapist.objects.all()

    def save(self):
        u = User.objects.create(username=self.cleaned_data["username"])
        Therapist.objects.create(user=u)
        
        u.first_name = self.cleaned_data["firstname"]
        u.last_name = self.cleaned_data["lastname"]
        u.email = self.cleaned_data["email"]
        u.is_active = self.cleaned_data["active"]
        if self.cleaned_data["password"]:
            u.set_password(self.cleaned_data["password"])

        try:
            therapist_group = Group.objects.get(name="therapist")
        except:
            therapist_group = Group.objects.create(name="therapist")

        u.groups.add(therapist_group)
        u.save()