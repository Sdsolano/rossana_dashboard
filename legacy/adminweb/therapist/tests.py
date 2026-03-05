from django.test import TestCase
from .models import Therapist,RangeAvailability
# Create your tests here.
from django.contrib.auth.models import Permission, User, Group
import datetime
import pytz

class TherapistTestCase(TestCase):

	def setUp(self):
		u = User.objects.create(username="test",email="chorizo@muybueno.com")
		Therapist.objects.create(user = u,timezone_verbose="America/Buenos_Aires")

	def make_weekrange(self,t):
		for i in range(0,7):
			r = RangeAvailability(therapist=t,weekday=i,begin=datetime.time(hour=20,minute=00),end=datetime.time(hour=23,minute=00))
			r.save()

	def make_weekrange_multiple(self,t):
		for i in range(0,7):
			RangeAvailability.objects.create(therapist=t,weekday=i,begin=datetime.time(10,00),end=datetime.time(13,00))
			RangeAvailability.objects.create(therapist=t,weekday=i,begin=datetime.time(15,00),end=datetime.time(18,00))
			

	def test01_getTherapistTest(self):
		
		t = Therapist.objects.get(user__username="test")
		self.assertEqual(t.user.username,"test")

	def test02_rangeavailibility_create(self):
		t = Therapist.objects.get(user__username="test")

		r = RangeAvailability(therapist=t,weekday=0,begin=datetime.time(hour=10,minute=00),end=datetime.time(hour=13,minute=00))
		r.save()

		self.assertEqual(len(t.rangeavailability_set.all()),1)
		self.assertEqual(t.rangeavailability_set.get(weekday=0).begin,datetime.time(10,00))


	def test03_weekrange(self):
		t = Therapist.objects.get(user__username="test")

		for i in range(0,7):
			r = RangeAvailability(therapist=t,weekday=i,begin=datetime.time(hour=10,minute=00),end=datetime.time(hour=13,minute=00))
			r.save()

		self.assertEqual(len(t.rangeavailability_set.all()),7)
		self.assertEqual(t.rangeavailability_set.get(weekday=0).begin,t.rangeavailability_set.get(weekday=1).begin)
		self.assertEqual(t.rangeavailability_set.get(weekday=1).begin,t.rangeavailability_set.get(weekday=2).begin)

	def test04_scheduler_and_test_first_meet(self):
			
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		rrange = t.rangeavailability_set.get(weekday=dt.weekday())

		t.scheduler(datetime.datetime(2024,7,16,10,0,0,tzinfo=pytz.timezone(t.timezone_verbose)),20)

		first_meet = t.meet_set.all()[0]
		first_dt = dt + datetime.timedelta(hours=rrange.begin.hour,minutes=rrange.begin.minute)

		self.assertEqual(len(t.meet_set.all()) > 0,True)

		self.assertEqual(first_meet.status,"F")
		self.assertEqual(first_meet.patient,None)
		self.assertEqual(first_meet.date,first_dt)
		self.assertEqual(first_meet.duration,20)

	def test05_scheduler_and_test_all_meet(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		rrange = t.rangeavailability_set.get(weekday=dt.weekday())

		t.scheduler(datetime.datetime(2024,7,16,10,0,0,tzinfo=pytz.timezone(t.timezone_verbose)),MEET_DURATION)

		ini_dt = dt + datetime.timedelta(hours=rrange.begin.hour,minutes=rrange.begin.minute)

		self.assertEqual(len(t.meet_set.all()) > 0,True)

		for m in t.meet_set.all():
			self.assertEqual(m.status,"F")
			self.assertEqual(m.patient,None)
			self.assertEqual(m.date,ini_dt)
			self.assertEqual(m.duration,MEET_DURATION)
			ini_dt += datetime.timedelta(minutes=MEET_DURATION)

	def test06_scheduler_and_more_than_one_range_per_day_len(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")

		self.make_weekrange_multiple(t)

		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		list_rrange = t.rangeavailability_set.filter(weekday=dt.weekday())

		self.assertEqual(len(list_rrange) > 1,True)



	def test07_scheduler_and_more_than_one_range_per_day(self):

		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange_multiple(t)
		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		list_rrange = t.rangeavailability_set.filter(weekday=dt.weekday())

		t.scheduler(datetime.datetime(2024,7,16,10,0,0,tzinfo=pytz.timezone(t.timezone_verbose)),MEET_DURATION)

		rrange = list_rrange[0]

		ini_dt = dt + datetime.timedelta(hours=rrange.begin.hour,minutes=rrange.begin.minute)

		self.assertEqual(len(t.meet_set.all()) > 0,True)
		
		for m in t.meet_set.all()[0:9]:
			self.assertEqual(m.status,"F")
			self.assertEqual(m.patient,None)
			self.assertEqual(m.date,ini_dt)
			self.assertEqual(m.duration,MEET_DURATION)
			ini_dt += datetime.timedelta(minutes=MEET_DURATION)

		rrange = list_rrange[1]

		ini_dt = dt + datetime.timedelta(hours=rrange.begin.hour,minutes=rrange.begin.minute)

		self.assertEqual(len(t.meet_set.all()) > 0,True)

		for m in t.meet_set.all()[9:]:
			self.assertEqual(m.status,"F")
			self.assertEqual(m.patient,None)
			self.assertEqual(m.date,ini_dt)
			self.assertEqual(m.duration,MEET_DURATION)
			ini_dt += datetime.timedelta(minutes=MEET_DURATION)

	def test08_make_schedule(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		now = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		rrange = t.rangeavailability_set.get(weekday=dt.weekday())

		
		t.make_schedule(now,3,MEET_DURATION)

		self.assertEqual(len(t.meet_set.filter(date__date=now.strftime("%Y-%m-%d"))) > 0,False)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=2)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=4)).strftime("%Y-%m-%d"))),0)


	def test09_make_schedule_2_times(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		now = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		rrange = t.rangeavailability_set.get(weekday=dt.weekday())

		
		t.make_schedule(now,3,MEET_DURATION)
		t.make_schedule(now,3,MEET_DURATION)

		self.assertEqual(len(t.meet_set.filter(date__date=now.strftime("%Y-%m-%d"))) > 0,False)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=2)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=4)).strftime("%Y-%m-%d"))),0)


	def test10_make_schedule_2_times_add_1_day(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		now = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		dt = datetime.datetime(2024,7,16,0,0,0,tzinfo=pytz.timezone(t.timezone_verbose))

		rrange = t.rangeavailability_set.get(weekday=dt.weekday())

		
		t.make_schedule(now,3,MEET_DURATION)
		t.make_schedule(now + datetime.timedelta(days=1),3,MEET_DURATION)

		self.assertEqual(len(t.meet_set.filter(date__date=now.strftime("%Y-%m-%d"))) > 0,False)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=2)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=4)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=5)).strftime("%Y-%m-%d"))),0)


	def test11_make_schedule_2_times_add_10_hours(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		now = datetime.datetime(2024,7,16,12,0,0,tzinfo=pytz.timezone(t.timezone_verbose))
		
		t.make_schedule(now,3,MEET_DURATION)
		t.make_schedule(now + datetime.timedelta(hours=11),3,MEET_DURATION)

		self.assertEqual(len(t.meet_set.filter(date__date=now.strftime("%Y-%m-%d"))) > 0,False)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=2)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))),9)
		self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=4)).strftime("%Y-%m-%d"))),0)
		#self.assertEqual(len(t.meet_set.filter(date__date=(now + datetime.timedelta(days=5)).strftime("%Y-%m-%d"))) == 0,True)


	def test12_show_free_meets(self):
		MEET_DURATION = 20
		t = Therapist.objects.get(user__username="test")
		self.make_weekrange(t)

		now = pytz.timezone(t.timezone_verbose).localize(datetime.datetime(2024,7,16,23,0,0))

		#print(t.timezone_verbose)
		#print(now)
		t.make_schedule(now,3,MEET_DURATION)

		tz_patient = "Europe/Paris"

		print(f"Now Therapist {now}")
		dt_patient = pytz.timezone(tz_patient).normalize(now)

		print(f"Now patient {dt_patient}")

		for m in t.meet_set.filter(status="F",date__date = (dt_patient + datetime.timedelta(days=1)).strftime("%Y-%m-%d")):
			#print(m.date)
			#print(pytz.timezone(t.timezone_verbose).normalize(m.date))
			print(f"{m.id} - {m.date} - {pytz.timezone(tz_patient).normalize(m.date)}")


		#for m in t.meet_set.all():
		#	print(f"{m.id} - {m.date} - {pytz.timezone(tz_patient).normalize(m.date)}")
















