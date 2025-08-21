from django.forms import *
from django.utils.translation import gettext_lazy as _


from .models import *
from patient.models import *
from therapist.models import *

class MeetCreateForm(Form):
    HORARIOS=(
        (1,"10:00 a 10:20"),
        (2,"10:20 a 10:40"),
        (3,"10:40 a 11:00"),
        (4,"11:00 a 11:20")
    )

    DAYS=(
        (1,"10:00 a 10:20"),
        (2,"10:20 a 10:40"),
        (3,"10:40 a 11:00"),
        (4,"11:00 a 11:20")
    )

    patient = ModelChoiceField(label=_('Paciente'),queryset=None,widget=Select(attrs={'class': 'form-control'}))
    therapist = ModelChoiceField(label=_('Terapeuta'),queryset=None,widget=Select(attrs={'class': 'form-control'}))
    #date = DateField(label=_('Dia'),widget=DateInput(attrs={'class': 'form-control'}))
    datechoice = ChoiceField(label=_('Dia'),choices=DAYS,widget=Select(attrs={'class': 'form-control'}))
    number = ChoiceField(label=_('Horario'),choices=HORARIOS,widget=Select(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.all()
        self.fields['therapist'].queryset = Therapist.objects.all()

        config = Config.objects.get(name="default")

        self.HORARIOS = []
        values = []
        for i in range(0,config.max_number()):
            self.HORARIOS.append((int(i),"{} a {}".format(config.make_meet_begin(i),config.make_meet_end(i))))

        self.DAYS= []

        for i in range(0,3):
            d = timezone.now() + timedelta(days=i+1)
            self.DAYS.append((int(i),d.date().strftime("%d/%m/%Y")))

        self.fields["datechoice"].choices = self.DAYS
        self.fields["number"].choices = self.HORARIOS

    def save(self):
        meet = Meet.objects.create(therapist=self.cleaned_data["therapist"],patient=self.cleaned_data["patient"])
        meet.date = self.cleaned_data["date"]
        meet.number = self.cleaned_data["number"]
        meet.update_cache()
        meet.save()



