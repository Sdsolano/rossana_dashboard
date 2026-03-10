from rest_framework import serializers

from therapist.models import Meet
from .models import Pay


class PayListSerializer(serializers.ModelSerializer):
    meet_id = serializers.IntegerField(source="meet.id", read_only=True)
    therapist_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Pay
        fields = [
            "id",
            "code",
            "meet_id",
            "therapist_name",
            "patient_name",
            "amount",
            "status",
            "timestamp",
        ]

    code = serializers.CharField(source="code", read_only=True)

    def get_therapist_name(self, obj):
        if not obj.meet or not obj.meet.therapist:
            return ""
        u = obj.meet.therapist.user
        return f"{u.first_name} {u.last_name}".strip() or u.username

    def get_patient_name(self, obj):
        if not obj.meet or not obj.meet.patient:
            return ""
        u = obj.meet.patient.user
        return f"{u.first_name} {u.last_name}".strip() or u.username


class PayCreateSerializer(serializers.Serializer):
    meet_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_code = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(choices=[c[0] for c in Pay.STATUS_CHOICES], default="P")

    def validate_meet_id(self, value):
        if not Meet.objects.filter(id=value).exists():
            raise serializers.ValidationError("La cita no existe.")
        return value

    def create(self, validated_data):
        meet = Meet.objects.get(id=validated_data["meet_id"])
        pay = Pay.objects.create(
            meet=meet,
            amount=validated_data["amount"],
            transaction_code=validated_data.get("transaction_code", ""),
            status=validated_data.get("status", "P"),
        )
        return pay


class PayDetailSerializer(serializers.ModelSerializer):
    meet_id = serializers.IntegerField(source="meet.id", read_only=True)
    code = serializers.CharField(source="code", read_only=True)

    class Meta:
        model = Pay
        fields = [
            "id",
            "code",
            "meet_id",
            "amount",
            "transaction_code",
            "status",
            "timestamp",
        ]


class PayUpdateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    transaction_code = serializers.CharField(max_length=255, required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=[c[0] for c in Pay.STATUS_CHOICES], required=False)

    def update(self, instance: Pay, validated_data):
        if "amount" in validated_data:
            instance.amount = validated_data["amount"]
        if "transaction_code" in validated_data:
            instance.transaction_code = validated_data["transaction_code"]
        if "status" in validated_data:
            instance.status = validated_data["status"]
        instance.save()
        return instance

    def create(self, validated_data):
        raise NotImplementedError

