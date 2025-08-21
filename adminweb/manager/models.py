from django.db import models

# Create your models here.
class Sidebar(models.Model):
    name = models.CharField(max_length=200,default="root",null=False)
    logo = models.ImageField(upload_to='manager',null=True)
    title = models.CharField(max_length=200,default="Nombre",null=True)
    def __str__(self):
        return self.name

class LoginPage(models.Model):
    name = models.CharField(max_length=200,default="root",null=False)
    logo = models.ImageField(upload_to='manager',null=True)
    title = models.CharField(max_length=200,default="Nombre",null=True)
    background = models.ImageField(upload_to='manager',null=True)
    def __str__(self):
        return self.name
