from django.db import models
from django.contrib.auth.models import Permission, User, Group
# Create your models here.

from django.utils import timezone
import pytz
from datetime import timedelta,datetime,time
from meet.models import Meet

class Therapist(models.Model):
	#person = models.ForeignKey(Person,on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	timezone = models.IntegerField(null=True,default=0)
	timezone_verbose = models.CharField(max_length=500,default="UTC")


	def __str__(self):
		return "#{} - {} {}".format(self.id,self.user.first_name,self.user.last_name)

	def verbose_name(self):
		return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"

	def availability(self,week_day):
		g = GridAvailability.objects.get(therapist=self)
		return GridAvailability.str_to_list(g.get_day_for_number(week_day))
		#return GridAvailability.str_to_list(g.friday)
	
	def availability_tz(self,week_day,tz_u):

		g = GridAvailability.objects.get(therapist=self)

		my_tz = g.timezone

		one_day_before = (week_day-1) % 7
		one_day_after = (week_day+1) % 7

		list_size = len(g.get_day_for_number(week_day))

		list_begin = list_size + int((tz_u - my_tz) / g.rate)
		list_end = list_begin + list_size

		#print(self.availability(week_day))
		#print(g.get_day_for_number(week_day))
		#print("{} {} {}".format(list_size,list_begin,list_end))

		cat_3days = g.get_day_for_number(one_day_after)+g.get_day_for_number(week_day)+g.get_day_for_number(one_day_before)
		#print(cat_3days)
		ret = cat_3days[list_begin:list_end]
		#print(ret)

		#return ()#(self.availability(week_day))#[list_begin:list_end]
		return GridAvailability.str_to_list(ret)


	def taked_meets_tz(self,day,tz_u):
		g = GridAvailability.objects.get(therapist=self)
		my_tz = g.timezone
		rate = g.rate
		list_size = len(g.get_day_for_number(0))


		meet_taked = self.meet_set.filter(date=day).exclude(status="C")
		ret = [(m.number - int((tz_u - my_tz) / rate)) % list_size for m in meet_taked]
		ret.sort()
		return ret

	def taked_meets(self,day):
		meet_taked = self.meet_set.filter(date=day).exclude(status="C")
		ret = [m.number for m in meet_taked]
		ret.sort()
		return ret

	def availible_meets(self,day):
		#los convierto en conjunto para realizar diferencia entre conjuntos
		return list(set(self.availability(day.weekday())).difference(set(self.taked_meets(day))))

	def availible_meets_between(self,begin,end):

		#los convierto en conjunto para realizar diferencia entre conjuntos
		return list(set(self.availability(day.weekday())).difference(set(self.taked_meets(day))))


	def availible_meets_tz(self,day,tz_u):
		#los convierto en conjunto para realizar diferencia entre conjuntos
		return list(set(self.availability_tz(day.weekday(),tz_u)).difference(set(self.taked_meets_tz(day,tz_u))))

	def tz(self):
		return GridAvailability.objects.get(therapist=self).timezone

	def get_timezone(self):
		
		g = GridAvailability.objects.get(therapist=self)
		signo="+"
		if g.timezone < 0:
			signo = "-"
		
		return "UTC{}{}:00".format(signo,abs(int(g.timezone/60)))


	def scheduler(self,date,meet_duration):
		weekday =  date.weekday()
		availability = self.rangeavailability_set.filter(weekday=weekday)

		meet_begin = None
		for date_range in availability:
			#if not start:

			#print(f"DATE QUE VIENE: {date}")
			date_range_begin = datetime(date.year,date.month,date.day,date_range.begin.hour,date_range.begin.minute,tzinfo=date.tzinfo)
			date_range_end = datetime(date.year,date.month,date.day,date_range.end.hour,date_range.end.minute,tzinfo=date.tzinfo)
			#print(date_range_begin)
			meet_begin = date_range_begin
			meet_end = meet_begin + timedelta(minutes=meet_duration)
			while meet_end <= date_range_end:
				s = Meet(therapist=self,date=meet_begin,duration=meet_duration,status="F")
				s.save()
				meet_begin = meet_end
				meet_end = meet_begin + timedelta(minutes=meet_duration)


	def make_schedule(self,dt_now,to_days,meet_duration):
		#config = Config.objects.get(name="default")
		#meet_duration = config.rate
		#now = pytz.timezone(self.timezone_verbose).normalize(timezone.now())
		#dt_from = now + timedelta(hours=25)
		dt_now += timedelta(days=1)
		for i in range(0,to_days):
			if len(self.meet_set.filter(date__date=dt_now.strftime("%Y-%m-%d"))) == 0:
				self.scheduler(dt_now,meet_duration)
			dt_now += timedelta(days=1)

	def rangear(self):
		g = self.gridavailability_set.all()[0]

		in_range = False
		aux_dt = datetime(2020,1,1,0,0)
		self.rangeavailability_set.all().delete()
		for i in range(0,7):
			rang = None

			for j in g.get_day_for_number(i):

				if not in_range and j == "1":
					in_range = True
					rang = RangeAvailability(therapist=self,weekday=i,begin=time(aux_dt.hour,aux_dt.minute))

				if in_range and j == "0":
					in_range = False
					rang.end = time(aux_dt.hour,aux_dt.minute)
					rang.save()
				aux_dt += timedelta(minutes=g.rate)



# class Schedule(models.Model):
# 	STATUS=(
#         ('EXPIRED',"Vencido"),
#         ('FREE',"Libre"),
#         ('ASSIGNED',"Asignado"),
#         ('TEMPORAL',"Temporal"),
# 	)

# 	therapist = models.ForeignKey(Therapist,on_delete=models.CASCADE)
# 	date = models.DateTimeField(null=False)
# 	duration = models.IntegerField(default=20) #in minutes 
# 	status =  models.CharField(max_length=10,choices=STATUS)


class RangeAvailability(models.Model):
	therapist = models.ForeignKey(Therapist,on_delete=models.CASCADE)
	weekday = models.IntegerField(default=20)
	begin = models.TimeField()
	end = models.TimeField()

	def __str__(self):
		number_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

		return f"{self.id} - {self.therapist.user.username} - {number_days[self.weekday]} - {self.begin} to {self.end}"


class GridAvailability(models.Model):
	therapist = models.ForeignKey(Therapist,on_delete=models.CASCADE)
	timezone = models.IntegerField(default=0) #timezone in minutes
	rate = models.IntegerField(default=20) #rate in minutes
	monday = models.CharField(max_length=1500)
	tuesday = models.CharField(max_length=1500)
	wednesday = models.CharField(max_length=1500)
	thursday = models.CharField(max_length=1500)
	friday = models.CharField(max_length=1500)
	saturday = models.CharField(max_length=1500)
	sunday = models.CharField(max_length=1500)


	def get_day_for_number(self,number):
		number_days = [self.monday,self.tuesday,self.wednesday,self.thursday,self.friday,self.saturday,self.sunday]

		return number_days[number]

	def set_day_for_number(self,number,data):
		if number == 0:
			self.monday = data
		if number == 1:
			self.tuesday = data
		if number == 2:
			self.wednesday = data
		if number == 3:
			self.thursday = data
		if number == 4:
			self.friday = data
		if number == 5:
			self.saturday = data
		if number == 6:
			self.sunday = data
		

	@staticmethod
	def str_to_list(s):
		d = s
		ret = []
		index = 0
		for t in d:
			if  t == '1':
				ret.append(index)
			index+=1
		return ret

	@staticmethod
	def list_to_str(l,max_length):
		#print(l)
		ret = ""
		for i in range(0,max_length):
			ret += ("1" if str(i) in l else "0")
		return ret


class Freeday(models.Model):
	therapist = models.ForeignKey(Therapist,on_delete=models.CASCADE)
	date = models.DateTimeField(null=False)

