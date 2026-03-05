


#class cronjobs(objects)
def cronjob_schedule():
	config = Config.objects.get(name="default")
    for t in Therapist.objects.filter(user__is_active=True):
        dt_now = pytz.timezone(t.timezone_verbose).normalize(timezone.now())
        t.make_schedule(dt_now,3,config.rate)