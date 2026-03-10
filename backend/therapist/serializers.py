from rest_framework import serializers
from django.contrib.auth.models import User, Group
from patient.models import Patient
from .models import Therapist, GridAvailability, ScheduleConfig, Meet
from .countries import timezone_verbose_to_minutes


def get_timezone_index(therapist):
    """Convierte therapist.timezone (minutos) a índice 0-23 (UTC-12 .. UTC+11)."""
    if therapist.timezone is None:
        return 12
    # timezone = (index - 12) * 60  =>  index = (timezone / 60) + 12
    idx = (therapist.timezone // 60) + 12
    return max(0, min(23, idx))


class TherapistListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Therapist
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "timezone_verbose",
        ]


class TherapistCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=1)
    password_confirm = serializers.CharField(write_only=True, min_length=1)
    is_active = serializers.BooleanField(default=True)
    timezone_verbose = serializers.CharField(max_length=100, required=False, default="")  # IANA ej. America/Argentina/Buenos_Aires
    monday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    tuesday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    wednesday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    thursday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    friday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    saturday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    sunday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya existe. Elija otro nombre.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "No coinciden las contraseñas."})
        return attrs

    def create(self, validated_data):
        config = ScheduleConfig.objects.filter(name="default").first()
        if not config:
            config = ScheduleConfig.objects.create(name="default", rate=40, interval=5)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_active=validated_data.get("is_active", True),
        )
        group, _ = Group.objects.get_or_create(name="therapist")
        user.groups.add(group)
        user.save()

        timezone_verbose = validated_data.get("timezone_verbose") or "UTC"
        tz_minutes = timezone_verbose_to_minutes(timezone_verbose)

        therapist = Therapist.objects.create(
            user=user,
            timezone=tz_minutes,
            timezone_verbose=timezone_verbose,
        )

        max_slots = config.max_number()
        rate = config.rate + config.interval
        GridAvailability.objects.create(
            therapist=therapist,
            timezone=tz_minutes,
            rate=rate,
            monday=GridAvailability.list_to_str(validated_data.get("monday", []), max_slots),
            tuesday=GridAvailability.list_to_str(validated_data.get("tuesday", []), max_slots),
            wednesday=GridAvailability.list_to_str(validated_data.get("wednesday", []), max_slots),
            thursday=GridAvailability.list_to_str(validated_data.get("thursday", []), max_slots),
            friday=GridAvailability.list_to_str(validated_data.get("friday", []), max_slots),
            saturday=GridAvailability.list_to_str(validated_data.get("saturday", []), max_slots),
            sunday=GridAvailability.list_to_str(validated_data.get("sunday", []), max_slots),
        )
        therapist.rangear()
        return therapist


class TherapistDetailSerializer(serializers.Serializer):
    """Detalle con disponibilidad para edición."""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    is_active = serializers.BooleanField(source="user.is_active")
    timezone_verbose = serializers.CharField()
    timezone_index = serializers.SerializerMethodField()
    monday = serializers.SerializerMethodField()
    tuesday = serializers.SerializerMethodField()
    wednesday = serializers.SerializerMethodField()
    thursday = serializers.SerializerMethodField()
    friday = serializers.SerializerMethodField()
    saturday = serializers.SerializerMethodField()
    sunday = serializers.SerializerMethodField()

    def get_timezone_index(self, obj):
        return get_timezone_index(obj)

    def _get_day_slots(self, obj, day_key):
        grid = getattr(obj, "grid", None)
        if not grid:
            try:
                grid = obj.gridavailability_set.first()
            except Exception:
                return []
        if not grid:
            return []
        day_str = getattr(grid, day_key, "") or ""
        return GridAvailability.str_to_list(day_str)

    def get_monday(self, obj):
        return self._get_day_slots(obj, "monday")

    def get_tuesday(self, obj):
        return self._get_day_slots(obj, "tuesday")

    def get_wednesday(self, obj):
        return self._get_day_slots(obj, "wednesday")

    def get_thursday(self, obj):
        return self._get_day_slots(obj, "thursday")

    def get_friday(self, obj):
        return self._get_day_slots(obj, "friday")

    def get_saturday(self, obj):
        return self._get_day_slots(obj, "saturday")

    def get_sunday(self, obj):
        return self._get_day_slots(obj, "sunday")


class TherapistUpdateSerializer(serializers.Serializer):
    """Actualización: user + grid (sin contraseña)."""
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    email = serializers.EmailField()
    is_active = serializers.BooleanField(default=True)
    timezone_verbose = serializers.CharField(max_length=100, required=False)
    monday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    tuesday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    wednesday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    thursday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    friday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    saturday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)
    sunday = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, default=list)

    def validate_username(self, value):
        instance = self.context.get("instance")
        if instance and instance.user.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya existe. Elija otro nombre.")
        return value

    def update(self, instance, validated_data):
        user = instance.user
        user.username = validated_data["username"]
        user.first_name = validated_data.get("first_name", "")
        user.last_name = validated_data.get("last_name", "")
        user.email = validated_data["email"]
        user.is_active = validated_data.get("is_active", True)
        user.save()

        if "timezone_verbose" in validated_data and validated_data["timezone_verbose"]:
            timezone_verbose = validated_data["timezone_verbose"]
            instance.timezone_verbose = timezone_verbose
            instance.timezone = timezone_verbose_to_minutes(timezone_verbose)
            instance.save()

        config = ScheduleConfig.objects.filter(name="default").first()
        if not config:
            config = ScheduleConfig.objects.create(name="default", rate=40, interval=5)
        max_slots = config.max_number()
        rate = config.rate + config.interval

        grid = instance.gridavailability_set.first()
        if not grid:
            grid = GridAvailability(therapist=instance, timezone=instance.timezone or 0, rate=rate)

        grid.rate = rate
        grid.timezone = instance.timezone or 0
        day_keys = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for key in day_keys:
            if key in validated_data:
                setattr(grid, key, GridAvailability.list_to_str(validated_data[key], max_slots))
        grid.save()
        instance.rangear()

        return instance


class MeetSerializer(serializers.ModelSerializer):
    therapist_id = serializers.IntegerField(source="therapist.id", read_only=True)
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Meet
        fields = [
            "id",
            "therapist_id",
            "patient_id",
            "patient_name",
            "date",
            "number",
            "status",
        ]

    def get_patient_name(self, obj):
        if not obj.patient:
            return ""
        u = obj.patient.user
        return f"{u.first_name} {u.last_name}".strip() or u.username


class MeetUpdateSerializer(serializers.Serializer):
    """Actualiza paciente y estado de una cita."""
    patient_id = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=[c[0] for c in Meet.STATUS_CHOICES], required=False)

    def update(self, instance, validated_data):
        patient_id = validated_data.get("patient_id", None)
        if "patient_id" in validated_data:
            if patient_id is None:
                instance.patient = None
            else:
                instance.patient = Patient.objects.filter(id=patient_id).first()
        if "status" in validated_data:
            instance.status = validated_data["status"]
        instance.save()
        return instance

    def create(self, validated_data):
        raise NotImplementedError


class TherapistPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=1)
    password_confirm = serializers.CharField(write_only=True, min_length=1)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "No coinciden las contraseñas."})
        return attrs

    def save(self, **kwargs):
        user = self.context["user"]
        user.set_password(self.validated_data["password"])
        user.save()
        return user
