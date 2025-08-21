from django.forms import *
from django.utils.translation import gettext_lazy as _


from .models import *


class LandingForm(Form):

    
    title = CharField(label=_('Título'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    promo = CharField(label=_('Promoción'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    hero_title = CharField(label=_('Sección Hero - Título'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    hero_subtitle = CharField(label=_('Sección Hero - Descripción'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    steps_title = CharField(label=_('Sección Pasos - Título'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    ready_title = CharField(label=_('Sección Preparado - Título'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    adv_title = CharField(label=_('Sección Ventajas - Título'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    adv_subtitle = CharField(label=_('Sección Ventajas - Descripción'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    faq_title = CharField(label=_('Sección FAQ - Título'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['patient'].queryset = Patient.objects.all()
        #self.fields['therapist'].queryset = Therapist.objects.all()

    def save(self):
        landing = Page.objects.get(name="landing")
        promo = SectionPromo.objects.get(name="promo")
        hero = SectionHero.objects.get(name="hero")
        steps = Section.objects.get(name="steps")
        ready = Section.objects.get(name="ready")
        faq = Section.objects.get(name="faq")
        adv = Section.objects.get(name="advantages")

        landing.title = self.cleaned_data["title"]
        promo.text = self.cleaned_data["promo"]
        hero.title = self.cleaned_data["hero_title"]
        hero.subtitle = self.cleaned_data["hero_subtitle"]
        steps.title = self.cleaned_data["steps_title"]
        ready.title = self.cleaned_data["ready_title"]
        adv.title = self.cleaned_data["adv_title"]
        adv.subtitle = self.cleaned_data["adv_subtitle"]
        faq.title = self.cleaned_data["faq_title"]
        
        landing.save()
        promo.save()
        hero.save()
        steps.save()
        faq.save()
        adv.save()
        ready.save()

    def load(self):
        landing = Page.objects.get(name="landing")
        promo = SectionPromo.objects.get(name="promo")
        hero = SectionHero.objects.get(name="hero")
        steps = Section.objects.get(name="steps")
        ready = Section.objects.get(name="ready")
        faq = Section.objects.get(name="faq")
        adv = Section.objects.get(name="advantages")

        self.fields["title"].initial = landing.title
        self.fields["promo"].initial = promo.text
        #self.fields["hero"].initial = patient.user.last_name
        self.fields["hero_title"].initial = hero.title
        self.fields["hero_subtitle"].initial = hero.subtitle
        self.fields["steps_title"].initial = steps.title
        self.fields["ready_title"].initial = ready.title
        self.fields["adv_title"].initial = adv.title
        self.fields["adv_subtitle"].initial = adv.subtitle
        self.fields["faq_title"].initial = faq.title
        
        


class StepForm(Form):
    
    title = CharField(label=_('Titulo'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    description = CharField(label=_('Descripción'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
       
    def __init__(self,instance, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.step = instance

        if self.step:
            self.fields["title"].initial = self.step.title
            self.fields["description"].initial = self.step.description

    def save(self):
        if self.step == None:
            self.step = Step()

        self.step.title = self.cleaned_data["title"]
        self.step.description = self.cleaned_data["description"]
        self.step.save()

        return self.step


class AdvantageForm(Form):
    
    title = CharField(label=_('Titulo'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    icon = CharField(label=_('Icono'),max_length=200,widget=TextInput(attrs={'class': 'form-control'}))
    description = CharField(label=_('Descripción'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
       
    def __init__(self,instance, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.advantage = instance

        if self.advantage:
            self.fields["icon"].initial = self.advantage.icon
            self.fields["title"].initial = self.advantage.title
            self.fields["description"].initial = self.advantage.description

    def save(self):
        if self.advantage == None:
            self.advantage = Advantage()

        self.advantage.title = self.cleaned_data["title"]
        self.advantage.description = self.cleaned_data["description"]
        self.advantage.icon = self.cleaned_data["icon"]
        self.advantage.save()

        return self.advantage

class FaqForm(Form):
    
    question = CharField(label=_('Pregunta'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
    answer = CharField(label=_('Respuesta'),max_length=1000,widget=TextInput(attrs={'class': 'form-control'}))
       
    def __init__(self,instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.faq = instance

        if self.faq:
            self.fields["question"].initial = self.faq.question
            self.fields["answer"].initial = self.faq.answer

    def save(self):
        if self.faq == None:
            section = Section.objects.get(name="faq")
            self.faq = FrequentQuestions(section=section)



        self.faq.question = self.cleaned_data["question"]
        self.faq.answer = self.cleaned_data["answer"]
        self.faq.save()

        return self.faq