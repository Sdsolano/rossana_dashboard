from django.forms import *
from django.utils.translation import gettext_lazy as _


from .models import *

class PatientAddForm(Form):
    username = CharField(label=_('Usuario'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    firstname = CharField(label=_('Nombre'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    lastname = CharField(label=_('Apellido'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(label=_('email'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    telephone = CharField(label=_('Telefono'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(label=_('Contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = CharField(label=_('Repetir contraseña'),max_length=200,widget=PasswordInput(attrs={'class': 'form-control'}))
    active = BooleanField(label=_('Activo'),required=False)
        #active = BooleanField(label="",initial=False,required=False,widget=PaperCheckboxInput(attrs={'label':_("Activo")}))

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
        p = Patient.objects.create(user=u)
        

        
        u.first_name = self.cleaned_data["firstname"]
        u.last_name = self.cleaned_data["lastname"]
        u.email = self.cleaned_data["email"]
        p.telephone = self.cleaned_data["telephone"]
        
        u.is_active = self.cleaned_data["active"]
        if self.cleaned_data["password"]:
            u.set_password(self.cleaned_data["password"])

        try:
            patient_group = Group.objects.get(name="patient")
        except:
            patient_group = Group.objects.create(name="patient")

        u.groups.add(patient_group)
        u.save()
        p.save()


    def load(self,patient):
        self.fields["username"].initial = patient.user.username
        self.fields["firstname"].initial = patient.user.first_name
        self.fields["lastname"].initial = patient.user.last_name
        self.fields["email"].initial = patient.user.email
        self.fields["telephone"].initial = patient.telephone
        self.fields["active"].initial = patient.user.is_active
        #self.fields["active"].initial = sheet.active
        #self.fields["categorie"].initial = sheet.categorie()

class PatientEditForm(Form):
    username = CharField(label=_('Usuario'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    firstname = CharField(label=_('Nombre'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    lastname = CharField(label=_('Apellido'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(label=_('email'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    telephone = CharField(label=_('Telefono'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    active = BooleanField(label=_('Activo'),required=False)


    #def clean_username(self):
    #    username = self.cleaned_data['username']
    #    if User.objects.filter(username=username).exists():
    #        raise ValidationError('El usuario ya existe. Elija otro nombre.')
    #    return username

        #active = BooleanField(label="",initial=False,required=False,widget=PaperCheckboxInput(attrs={'label':_("Activo")}))
    def save(self,patient):
        u = patient.user
        u.username = self.cleaned_data["username"]
        u.first_name = self.cleaned_data["firstname"]
        u.last_name = self.cleaned_data["lastname"]
        u.email = self.cleaned_data["email"]
        patient.telephone = self.cleaned_data["telephone"]
        u.is_active = self.cleaned_data["active"]
        u.save()
        patient.save()

    def load(self,patient):
        self.fields["username"].initial = patient.user.username
        self.fields["firstname"].initial = patient.user.first_name
        self.fields["lastname"].initial = patient.user.last_name
        self.fields["email"].initial = patient.user.email
        self.fields["telephone"].initial = patient.telephone
        self.fields["active"].initial = patient.user.is_active


class PatientPasswordForm(Form):
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

