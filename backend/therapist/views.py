from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import Therapist, ScheduleConfig, Freeday, Meet
from .countries import get_countries_for_api
from .serializers import (
    TherapistListSerializer,
    TherapistCreateSerializer,
    TherapistDetailSerializer,
    TherapistUpdateSerializer,
    TherapistPasswordSerializer,
)


def get_schedule_config_response():
    config = ScheduleConfig.objects.filter(name="default").first()
    if not config:
        config = ScheduleConfig.objects.create(name="default", rate=40, interval=5)
    max_n = config.max_number()
    slots = []
    base = datetime(1990, 1, 1)
    for i in range(max_n):
        begin = base + config.make_meet_begin(i)
        end = base + config.make_meet_end(i)
        slots.append({"id": i, "label": f"{begin.strftime('%H:%M')} a {end.strftime('%H:%M')}"})
    return Response({
        "rate": config.rate,
        "interval": config.interval,
        "max_number": max_n,
        "slots": slots,
        "timezones": [f"UTC{i}:00" for i in range(-12, 0)] + [f"UTC+{i}:00" for i in range(0, 12)],
        "countries": get_countries_for_api(),
    })


class ScheduleConfigAPIView(APIView):
    def get(self, request):
        return get_schedule_config_response()


class TherapistListAPIView(APIView):
    def get(self, request):
        qs = Therapist.objects.all().select_related("user")
        serializer = TherapistListSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TherapistCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        therapist = serializer.save()
        out = TherapistListSerializer(therapist)
        return Response(out.data, status=status.HTTP_201_CREATED)


class TherapistDetailAPIView(APIView):
    def get(self, request, pk):
        therapist = get_object_or_404(
            Therapist.objects.prefetch_related("gridavailability_set").select_related("user"),
            pk=pk,
        )
        serializer = TherapistDetailSerializer(therapist)
        return Response(serializer.data)

    def put(self, request, pk):
        therapist = get_object_or_404(
            Therapist.objects.prefetch_related("gridavailability_set").select_related("user"),
            pk=pk,
        )
        serializer = TherapistUpdateSerializer(
            therapist,
            data=request.data,
            partial=False,
            context={"instance": therapist},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        out = TherapistListSerializer(therapist)
        return Response(out.data)

    def patch(self, request, pk):
        therapist = get_object_or_404(
            Therapist.objects.prefetch_related("gridavailability_set").select_related("user"),
            pk=pk,
        )
        serializer = TherapistUpdateSerializer(
            therapist,
            data=request.data,
            partial=True,
            context={"instance": therapist},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        out = TherapistListSerializer(therapist)
        return Response(out.data)

    def delete(self, request, pk):
        therapist = get_object_or_404(Therapist.objects.select_related("user"), pk=pk)
        user = therapist.user
        therapist.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TherapistPasswordAPIView(APIView):
    def post(self, request, pk):
        therapist = get_object_or_404(Therapist.objects.select_related("user"), pk=pk)
        serializer = TherapistPasswordSerializer(
            data=request.data,
            context={"user": therapist.user},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"detail": "Contraseña actualizada."})


class TherapistActivateAPIView(APIView):
    def post(self, request, pk):
        therapist = get_object_or_404(Therapist.objects.select_related("user"), pk=pk)
        therapist.user.is_active = True
        therapist.user.save()
        return Response(TherapistListSerializer(therapist).data)


class TherapistDeactivateAPIView(APIView):
    def post(self, request, pk):
        therapist = get_object_or_404(Therapist.objects.select_related("user"), pk=pk)
        therapist.user.is_active = False
        therapist.user.save()
        return Response(TherapistListSerializer(therapist).data)


class TherapistAvailabilityAPIView(APIView):
    """GET ?week_day=0 | ?date=YYYY-MM-DD [&tz_minutes=-180]"""

    def get(self, request, pk):
        therapist = get_object_or_404(
            Therapist.objects.prefetch_related("gridavailability_set"),
            pk=pk,
        )
        week_day = request.query_params.get("week_day")
        date_str = request.query_params.get("date")
        tz_minutes = request.query_params.get("tz_minutes", type=int)

        if week_day is not None:
            try:
                wd = int(week_day)
                if 0 <= wd <= 6:
                    if tz_minutes is not None:
                        data = {"availability": therapist.availability_tz(wd, tz_minutes)}
                    else:
                        data = {"availability": therapist.availability(wd)}
                    return Response(data)
            except (ValueError, TypeError):
                pass
            return Response({"detail": "week_day debe ser 0-6."}, status=status.HTTP_400_BAD_REQUEST)

        if date_str:
            from datetime import datetime as dt
            try:
                day = dt.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"detail": "date debe ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            if tz_minutes is not None:
                return Response({
                    "availible_meets": therapist.availible_meets_tz(day, tz_minutes),
                    "taked_meets": therapist.taked_meets_tz(day, tz_minutes),
                })
            return Response({
                "availible_meets": therapist.availible_meets(day),
                "taked_meets": therapist.taked_meets(day),
            })

        return Response(
            {"detail": "Indica week_day (0-6) o date (YYYY-MM-DD)."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TherapistFreedaysAPIView(APIView):
    """Días bloqueados: GET list/check, POST lock, DELETE unlock."""

    def get(self, request, pk):
        therapist = get_object_or_404(Therapist, pk=pk)
        date_str = request.query_params.get("date")
        if date_str:
            try:
                day = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "date debe ser YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            locked = therapist.freeday_set.filter(date=day).exists()
            return Response({"locked": locked})

        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        qs = therapist.freeday_set.all().order_by("date")
        if from_date:
            try:
                qs = qs.filter(date__gte=datetime.strptime(from_date, "%Y-%m-%d").date())
            except ValueError:
                pass
        if to_date:
            try:
                qs = qs.filter(date__lte=datetime.strptime(to_date, "%Y-%m-%d").date())
            except ValueError:
                pass
        dates = [fd.date.strftime("%Y-%m-%d") for fd in qs]
        return Response({"dates": dates})

    def post(self, request, pk):
        therapist = get_object_or_404(Therapist, pk=pk)
        date_str = request.data.get("date")
        if not date_str:
            return Response(
                {"detail": "Indica date (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "date debe ser YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Freeday.objects.get_or_create(therapist=therapist, date=day)
        return Response({"date": date_str, "locked": True}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk):
        therapist = get_object_or_404(Therapist, pk=pk)
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "Indica date (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "date debe ser YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        therapist.freeday_set.filter(date=day).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----- Auth y panel terapeuta -----


class AuthLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"detail": "Indica username y password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {"detail": "Usuario o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        therapist = Therapist.objects.filter(user=user).first()
        if not therapist:
            return Response(
                {"detail": "No eres un terapeuta registrado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "therapist_id": therapist.id,
            "username": user.username,
        })


class MeAPIView(APIView):
    """Panel del terapeuta: datos + agenda 7 días. Requiere auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        therapist = Therapist.objects.filter(user=request.user).select_related("user").first()
        if not therapist:
            return Response(
                {"detail": "No eres un terapeuta."},
                status=status.HTTP_403_FORBIDDEN,
            )
        today = datetime.now().date()
        days = []
        for i in range(7):
            day = today + timedelta(days=i)
            meets = list(
                therapist.meet_set.filter(date=day, status="D")
                .order_by("number")
                .values("id", "number", "status")
            )
            locked = therapist.freeday_set.filter(date=day).exists()
            label = "Hoy" if i == 0 else day.strftime("%d/%m")
            days.append({
                "date": day.strftime("%Y-%m-%d"),
                "label": label,
                "meets": meets,
                "locked": locked,
            })
        return Response({
            "therapist": TherapistListSerializer(therapist).data,
            "days": days,
        })


class MeAvailabilityAPIView(APIView):
    """GET/PUT mi disponibilidad (terapeuta logueado)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        therapist = Therapist.objects.filter(user=request.user).prefetch_related("gridavailability_set").first()
        if not therapist:
            return Response({"detail": "No eres un terapeuta."}, status=status.HTTP_403_FORBIDDEN)
        return Response(TherapistDetailSerializer(therapist).data)

    def put(self, request):
        therapist = Therapist.objects.filter(user=request.user).prefetch_related("gridavailability_set").first()
        if not therapist:
            return Response({"detail": "No eres un terapeuta."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TherapistUpdateSerializer(
            therapist,
            data=request.data,
            partial=False,
            context={"instance": therapist},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(TherapistListSerializer(therapist).data)


class TherapistGenerateScheduleAPIView(APIView):
    """POST genera slots libres (F) para los próximos N días."""

    def post(self, request, pk):
        therapist = get_object_or_404(Therapist.objects.prefetch_related("rangeavailability_set"), pk=pk)
        config = ScheduleConfig.objects.filter(name="default").first()
        if not config:
            config = ScheduleConfig.objects.create(name="default", rate=40, interval=5)
        meet_duration = config.rate + config.interval
        to_days = request.data.get("days", 3)
        try:
            to_days = int(to_days)
            to_days = max(1, min(30, to_days))
        except (TypeError, ValueError):
            to_days = 3
        from django.utils import timezone
        therapist.make_schedule(timezone.now(), to_days, meet_duration)
        return Response({"detail": f"Agenda generada para {to_days} días."})
