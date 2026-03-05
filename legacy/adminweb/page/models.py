from django.db import models

# Create your models here.
class Page(models.Model):
	name = models.CharField(max_length=200,default="")
	title = models.CharField(max_length=1000,default="")

	def __str__(self):
		return self.name

class Section(models.Model):
	page = models.ForeignKey(Page,on_delete=models.CASCADE)
	name = models.CharField(max_length=200,default="")
	title = models.CharField(max_length=1000,default="")
	subtitle = models.CharField(max_length=1000,default="")
	
	def __str__(self):
		return self.name

class SectionPromo(Section):
	text = models.CharField(max_length=1000,default="")

class SectionHero(Section):
	image = models.ImageField(upload_to='section/hero',null=True)

class Step(models.Model):
	section = models.ForeignKey(Section,on_delete=models.CASCADE)
	number = models.IntegerField(default=1)
	title = models.CharField(max_length=1000,default="")
	description = models.CharField(max_length=1000,default="")

class Advantage(models.Model):
	section = models.ForeignKey(Section,on_delete=models.CASCADE)
	order = models.IntegerField(default=1)
	icon = models.CharField(max_length=1000,default="")
	title = models.CharField(max_length=1000,default="")
	description = models.CharField(max_length=1000,default="")

class Testimony(models.Model):
	section = models.ForeignKey(Section,on_delete=models.CASCADE)
	testimony = models.CharField(max_length=1000,default="")
	stars = models.IntegerField(default=5)
	client_name = models.CharField(max_length=100,default="")
	image = models.ImageField(upload_to='section/photo',null=True)

class FrequentQuestions(models.Model):
	section = models.ForeignKey(Section,on_delete=models.CASCADE)
	question = models.CharField(max_length=1000,default="")
	answer = models.CharField(max_length=1000,default="")
