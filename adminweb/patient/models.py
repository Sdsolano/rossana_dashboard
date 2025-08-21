from django.db import models

from django.contrib.auth.models import Permission, User, Group
# Create your models here.



class Patient(models.Model):
	#person = models.ForeignKey(Person,on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	telephone = models.CharField(max_length=200,default="")
	timezone = models.IntegerField(null=True,default=0)
	timezone_verbose = models.CharField(max_length=1000,default="UTC+00:00")

	def __str__(self):
		return "#{} - {} {}".format(self.id,self.user.first_name,self.user.last_name)

	def verbose_name(self):
		return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"
	
	def meets_confirmed(self):
		return self.meet_set.filter(status="D")

	def meets_canceled(self):
		return self.meet_set.filter(status="C")

	def meets_absent(self):
		return self.meet_set.filter(status="A")


	@staticmethod
	def make_username(user):
		username = user.first_name[0]+user.last_name
		username = username.lower()
		count = User.objects.filter(username__startswith=username).count()

		#si no soy yo y hay alguien mas modifica el username generado para que no se repita con otro
		if username != user.username and count > 0:
			username += str(count)

		return username
