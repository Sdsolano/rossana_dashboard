from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=200, default="", blank=True)
    timezone = models.IntegerField(null=True, default=0)
    timezone_verbose = models.CharField(max_length=500, default="UTC")

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return "#{} - {} {}".format(self.id, self.user.first_name, self.user.last_name)

    def verbose_name_display(self):
        return "{} {} ({})".format(self.user.first_name, self.user.last_name, self.user.username)

