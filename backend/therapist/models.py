from django.db import models
from django.contrib.auth.models import User
from datetime import time, timedelta, datetime


class ScheduleConfig(models.Model):
    """Configuración de intervalos para agendas (rate + interval en minutos)."""
    name = models.CharField(max_length=100, default="default")
    rate = models.IntegerField(default=40)  # duración cita en minutos
    interval = models.IntegerField(default=5)  # intervalo entre citas en minutos

    class Meta:
        verbose_name = "Configuración de agenda"
        verbose_name_plural = "Configuraciones de agenda"

    def max_number(self):
        minutes_of_a_day = 24 * 60
        return int(minutes_of_a_day / (self.rate + self.interval))

    def make_meet_begin(self, number):
        return timedelta(minutes=number * (self.rate + self.interval))

    def make_meet_end(self, number):
        slot_end = timedelta(minutes=(number + 1) * (self.rate + self.interval))
        if slot_end < timedelta(days=1):
            return slot_end
        return slot_end - timedelta(days=1)


class Therapist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timezone = models.IntegerField(null=True, default=0)
    timezone_verbose = models.CharField(max_length=500, default="UTC")

    class Meta:
        verbose_name = "Terapeuta"
        verbose_name_plural = "Terapeutas"

    def __str__(self):
        return "#{} - {} {}".format(
            self.id, self.user.first_name, self.user.last_name
        )

    def verbose_name_display(self):
        return "{} {} ({})".format(
            self.user.first_name, self.user.last_name, self.user.username
        )

    def availability(self, week_day):
        """Slots disponibles (índices) para un día de la semana (0=lunes, 6=domingo)."""
        g = self.gridavailability_set.first()
        if not g:
            return []
        day_str = g.get_day_for_number(week_day) or ""
        return GridAvailability.str_to_list(day_str)

    def availability_tz(self, week_day, tz_u):
        """Slots disponibles para week_day en la zona horaria tz_u (minutos)."""
        g = self.gridavailability_set.first()
        if not g:
            return []
        my_tz = g.timezone
        one_day_before = (week_day - 1) % 7
        one_day_after = (week_day + 1) % 7
        list_size = len(g.get_day_for_number(week_day) or "")
        list_begin = list_size + int((tz_u - my_tz) / g.rate)
        list_end = list_begin + list_size
        cat_3days = (
            (g.get_day_for_number(one_day_after) or "")
            + (g.get_day_for_number(week_day) or "")
            + (g.get_day_for_number(one_day_before) or "")
        )
        ret = cat_3days[list_begin:list_end]
        return GridAvailability.str_to_list(ret)

    def taked_meets(self, day):
        """Índices de slot ya ocupados en ese día (excl. cancelados)."""
        meets = self.meet_set.filter(date=day).exclude(status="C")
        return sorted([m.number for m in meets])

    def taked_meets_tz(self, day, tz_u):
        """Índices de slot ocupados en day para la zona tz_u."""
        g = self.gridavailability_set.first()
        if not g:
            return self.taked_meets(day)
        my_tz = g.timezone
        rate = g.rate
        list_size = len(g.get_day_for_number(0) or "")
        if list_size == 0:
            return []
        meets = self.meet_set.filter(date=day).exclude(status="C")
        ret = [(m.number - int((tz_u - my_tz) / rate)) % list_size for m in meets]
        return sorted(set(ret))

    def availible_meets(self, day):
        """Slots libres en day (disponibilidad − ocupados)."""
        avail = set(self.availability(day.weekday()))
        taken = set(self.taked_meets(day))
        return sorted(avail - taken)

    def availible_meets_tz(self, day, tz_u):
        """Slots libres en day para zona horaria tz_u."""
        avail = set(self.availability_tz(day.weekday(), tz_u))
        taken = set(self.taked_meets_tz(day, tz_u))
        return sorted(avail - taken)

    def rangear(self):
        """Reconstruye RangeAvailability a partir del Grid del terapeuta."""
        grids = self.gridavailability_set.all()
        if not grids:
            return
        g = grids[0]
        self.rangeavailability_set.all().delete()
        for i in range(7):
            day_str = g.get_day_for_number(i) or ""
            aux_minutes = 0
            in_range = False
            rang = None
            for j in day_str:
                if not in_range and j == "1":
                    in_range = True
                    h, m = divmod(aux_minutes, 60)
                    rang = RangeAvailability(
                        therapist=self, weekday=i, begin=time(h, m)
                    )
                if in_range and j == "0":
                    in_range = False
                    h, m = divmod(aux_minutes, 60)
                    rang.end = time(h, m)
                    rang.save()
                aux_minutes += g.rate

    def scheduler(self, day, meet_duration):
        """Crea Meet(status='F') para cada slot de disponibilidad en day (date)."""
        g = self.gridavailability_set.first()
        if not g:
            return
        weekday = day.weekday()
        for date_range in self.rangeavailability_set.filter(weekday=weekday):
            begin_min = date_range.begin.hour * 60 + date_range.begin.minute
            end_min = date_range.end.hour * 60 + date_range.end.minute
            slot = begin_min
            while slot + meet_duration <= end_min:
                slot_number = slot // g.rate
                Meet.objects.get_or_create(
                    therapist=self,
                    date=day,
                    number=slot_number,
                    defaults={"status": "F"},
                )
                slot += meet_duration

    def make_schedule(self, dt_now, to_days, meet_duration):
        """Genera slots libres para los próximos to_days días (empezando mañana)."""
        start = dt_now.date() + timedelta(days=1)
        for i in range(to_days):
            day = start + timedelta(days=i)
            if not self.meet_set.filter(date=day).exists():
                self.scheduler(day, meet_duration)


class Meet(models.Model):
    """Cita/slot asignado."""
    STATUS_CHOICES = [
        ("F", "Libre"),
        ("T", "Temporal"),
        ("U", "Pago pendiente"),
        ("D", "Confirmado"),
        ("R", "Reprogramado"),
        ("C", "Cancelado"),
        ("P", "Presente"),
        ("A", "Ausente"),
    ]
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    # Paciente opcional asociado a la cita (None si el slot sigue libre)
    patient = models.ForeignKey("patient.Patient", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    number = models.IntegerField()  # índice de slot en el día
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="F")

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"


class GridAvailability(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    timezone = models.IntegerField(default=0)  # minutes
    rate = models.IntegerField(default=20)  # minutes
    monday = models.CharField(max_length=1500, default="")
    tuesday = models.CharField(max_length=1500, default="")
    wednesday = models.CharField(max_length=1500, default="")
    thursday = models.CharField(max_length=1500, default="")
    friday = models.CharField(max_length=1500, default="")
    saturday = models.CharField(max_length=1500, default="")
    sunday = models.CharField(max_length=1500, default="")

    def get_day_for_number(self, number):
        days = [
            self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.sunday,
        ]
        return days[number]

    def set_day_for_number(self, number, data):
        if number == 0:
            self.monday = data
        elif number == 1:
            self.tuesday = data
        elif number == 2:
            self.wednesday = data
        elif number == 3:
            self.thursday = data
        elif number == 4:
            self.friday = data
        elif number == 5:
            self.saturday = data
        elif number == 6:
            self.sunday = data

    @staticmethod
    def str_to_list(s):
        ret = []
        for i, t in enumerate(s or ""):
            if t == "1":
                ret.append(i)
        return ret

    @staticmethod
    def list_to_str(lst, max_length):
        return "".join("1" if i in lst else "0" for i in range(max_length))


class RangeAvailability(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    weekday = models.IntegerField(default=0)
    begin = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        return "{} - {} {} a {}".format(
            self.therapist_id, days[self.weekday], self.begin, self.end
        )


class Freeday(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        verbose_name = "Día libre"
        verbose_name_plural = "Días libres"
