from django.contrib.auth.models import Group, User
from rest_framework import serializers

from therapist.countries import timezone_verbose_to_minutes
from .models import Patient


def get_timezone_index(patient: Patient) -> int:
    """Convierte patient.timezone (minutos) a índice 0-23 (UTC-12 .. UTC+11)."""
    if patient.timezone is None:
        return 12
    idx = (patient.timezone // 60) + 12
    return max(0, min(23, idx))


class PatientListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "telephone",
            "timezone_verbose",
        ]


class PatientCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=1)
    password_confirm = serializers.CharField(write_only=True, min_length=1)
    is_active = serializers.BooleanField(default=True)
    telephone = serializers.CharField(max_length=200, required=False, default="")
    timezone_verbose = serializers.CharField(max_length=100, required=False, default="")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya existe. Elija otro nombre.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "No coinciden las contraseñas."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_active=validated_data.get("is_active", True),
        )
        group, _ = Group.objects.get_or_create(name="patient")
        user.groups.add(group)
        user.save()

        timezone_verbose = validated_data.get("timezone_verbose") or "UTC"
        tz_minutes = timezone_verbose_to_minutes(timezone_verbose)

        patient = Patient.objects.create(
            user=user,
            telephone=validated_data.get("telephone", ""),
            timezone=tz_minutes,
            timezone_verbose=timezone_verbose,
        )
        return patient


class PatientDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    is_active = serializers.BooleanField(source="user.is_active")
    telephone = serializers.CharField()
    timezone_verbose = serializers.CharField()
    timezone_index = serializers.SerializerMethodField()

    def get_timezone_index(self, obj: Patient) -> int:
        return get_timezone_index(obj)


class PatientUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    email = serializers.EmailField()
    is_active = serializers.BooleanField(default=True)
    telephone = serializers.CharField(max_length=200, required=False, default="")
    timezone_verbose = serializers.CharField(max_length=100, required=False)

    def validate_username(self, value):
        instance: Patient | None = self.context.get("instance")
        if instance and instance.user.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya existe. Elija otro nombre.")
        return value

    def update(self, instance: Patient, validated_data):
        user = instance.user
        user.username = validated_data["username"]
        user.first_name = validated_data.get("first_name", "")
        user.last_name = validated_data.get("last_name", "")
        user.email = validated_data["email"]
        user.is_active = validated_data.get("is_active", True)
        user.save()

        instance.telephone = validated_data.get("telephone", instance.telephone)

        if "timezone_verbose" in validated_data and validated_data["timezone_verbose"]:
            timezone_verbose = validated_data["timezone_verbose"]
            instance.timezone_verbose = timezone_verbose
            instance.timezone = timezone_verbose_to_minutes(timezone_verbose)

        instance.save()
        return instance

