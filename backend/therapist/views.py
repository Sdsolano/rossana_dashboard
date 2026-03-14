from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from .models import Therapist, ScheduleConfig, Freeday, Meet
from .countries import timezone_verbose_to_minutes
from patient.models import Patient
from .countries import get_countries_for_api
from .serializers import (
    TherapistListSerializer,
    TherapistCreateSerializer,
    TherapistDetailSerializer,
    TherapistUpdateSerializer,
    TherapistPasswordSerializer,
    MeetSerializer,
    MeetUpdateSerializer,
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
        raw_tz = request.query_params.get("tz_minutes")
        tz_minutes = None
        if raw_tz is not None:
            try:
                tz_minutes = int(raw_tz)
            except (TypeError, ValueError):
                pass

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


class MeetListAPIView(APIView):
    """Listado de citas (opcionalmente filtradas por terapeuta y fecha)."""

    def get(self, request):
        qs = Meet.objects.select_related("therapist", "patient__user").all().order_by("date", "number")
        therapist_id = request.query_params.get("therapist")
        date_str = request.query_params.get("date")
        if therapist_id:
            try:
                qs = qs.filter(therapist_id=int(therapist_id))
            except (TypeError, ValueError):
                pass
        if date_str:
            try:
                day = datetime.strptime(date_str, "%Y-%m-%d").date()
                qs = qs.filter(date=day)
            except ValueError:
                pass
        return Response(MeetSerializer(qs, many=True).data)


class MeetDetailAPIView(APIView):
    """Detalle y actualización sencilla de una cita."""

    def get(self, request, pk):
        meet = get_object_or_404(Meet.objects.select_related("therapist", "patient__user"), pk=pk)
        return Response(MeetSerializer(meet).data)

    def put(self, request, pk):
        meet = get_object_or_404(Meet.objects.select_related("therapist", "patient__user"), pk=pk)
        serializer = MeetUpdateSerializer(meet, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(MeetSerializer(meet).data)


class MeetBookAPIView(APIView):
    """Reserva una cita: asigna paciente y cambia estado en un slot libre."""

    def post(self, request):
        therapist_id = request.data.get("therapist_id")
        patient_id = request.data.get("patient_id")
        date_str = request.data.get("date")
        number = request.data.get("number")

        if not (therapist_id and patient_id and date_str is not None and number is not None):
            return Response(
                {"detail": "Indica therapist_id, patient_id, date (YYYY-MM-DD) y number."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            therapist_id = int(therapist_id)
            patient_id = int(patient_id)
            number = int(number)
        except (TypeError, ValueError):
            return Response({"detail": "IDs y number deben ser enteros."}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import datetime as dt

        try:
            day = dt.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "date debe ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        therapist = get_object_or_404(Therapist, pk=therapist_id)
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=patient_id)

        meet = (
            Meet.objects.select_for_update()
            .filter(therapist=therapist, date=day, number=number, status="F")
            .first()
        )
        if not meet:
            return Response(
                {"detail": "No hay un slot libre con esos datos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        meet.patient = patient
        meet.status = "D"
        meet.save()
        return Response(MeetSerializer(meet).data, status=status.HTTP_200_OK)


def _slot_labels():
    """Lista de { id: number, label } según config por defecto."""
    config = ScheduleConfig.objects.filter(name="default").first()
    if not config:
        config = ScheduleConfig.objects.create(name="default", rate=40, interval=5)
    base = datetime(1990, 1, 1)
    max_n = config.max_number()
    return [
        {"id": i, "label": f"{ (base + config.make_meet_begin(i)).strftime('%H:%M') } a { (base + config.make_meet_end(i)).strftime('%H:%M') }"}
        for i in range(max_n)
    ]


class GlobalAvailabilityAPIView(APIView):
    """GET ?date=YYYY-MM-DD [&therapist_id=] [&tz_minutes=] [&timezone_verbose=] — slots disponibles."""

    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "Indica date (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "date debe ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        raw_therapist_id = request.query_params.get("therapist_id")
        raw_tz_minutes = request.query_params.get("tz_minutes")
        therapist_id = None
        if raw_therapist_id is not None:
            try:
                therapist_id = int(raw_therapist_id)
            except (TypeError, ValueError):
                pass
        tz_minutes = None
        if raw_tz_minutes is not None:
            try:
                tz_minutes = int(raw_tz_minutes)
            except (TypeError, ValueError):
                pass
        tz_verbose = (request.query_params.get("timezone_verbose") or "").strip()
        if tz_verbose and tz_minutes is None:
            tz_minutes = timezone_verbose_to_minutes(tz_verbose)
        try:
            therapists = Therapist.objects.filter(user__is_active=True).select_related("user")
            if therapist_id is not None:
                therapists = therapists.filter(pk=therapist_id)
            labels_by_number = {s["id"]: s["label"] for s in _slot_labels()}
            slots = []
            for t in therapists:
                if t.freeday_set.filter(date=day).exists():
                    continue
                try:
                    if tz_minutes is not None:
                        avail = t.availible_meets_tz(day, tz_minutes)
                    else:
                        avail = t.availible_meets(day)
                except Exception:
                    avail = []
                name = f"{t.user.first_name or ''} {t.user.last_name or ''}".strip() or t.user.username
                for num in avail:
                    slots.append({
                        "therapist_id": t.id,
                        "therapist_name": name,
                        "number": num,
                        "label": labels_by_number.get(num, str(num)),
                    })
            slots.sort(key=lambda x: (x["therapist_name"], x["number"]))
            return Response({"slots": slots})
        except Exception as e:
            return Response(
                {"detail": f"Error al obtener disponibilidad: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def _get_or_create_patient(email, first_name, last_name, telephone, timezone_verbose):
    """Obtiene paciente por email o crea User + Patient (sin contraseña útil)."""
    user = User.objects.filter(email=email).first()
    if user:
        patient = Patient.objects.filter(user=user).first()
        if patient:
            if timezone_verbose:
                patient.timezone_verbose = timezone_verbose
                patient.timezone = timezone_verbose_to_minutes(timezone_verbose)
                patient.save()
            return patient
        patient = Patient.objects.create(
            user=user,
            telephone=telephone or "",
            timezone_verbose=timezone_verbose or "UTC",
        )
        if timezone_verbose:
            patient.timezone = timezone_verbose_to_minutes(timezone_verbose)
            patient.save()
        return patient
    base_username = (str(first_name or "")[:1] + str(last_name or "")).lower().replace(" ", "") or email.split("@")[0]
    username = base_username
    c = 0
    while User.objects.filter(username=username).exists():
        c += 1
        username = f"{base_username}{c}"
    user = User.objects.create(
        username=username,
        email=email,
        first_name=first_name or "",
        last_name=last_name or "",
        is_active=True,
    )
    user.set_unusable_password()
    user.save()
    group, _ = Group.objects.get_or_create(name="patient")
    user.groups.add(group)
    tz_verbose = timezone_verbose or "UTC"
    tz_minutes = timezone_verbose_to_minutes(tz_verbose)
    patient = Patient.objects.create(
        user=user,
        telephone=telephone or "",
        timezone=tz_minutes,
        timezone_verbose=tz_verbose,
    )
    return patient


class MeetSolicitarAPIView(APIView):
    """POST reserva pública: therapist_id, date, number + datos paciente (first_name, last_name, email, telephone)."""

    def post(self, request):
        therapist_id = request.data.get("therapist_id")
        date_str = request.data.get("date")
        number = request.data.get("number")
        first_name = request.data.get("first_name", "").strip()
        last_name = request.data.get("last_name", "").strip()
        email = (request.data.get("email") or "").strip()
        telephone = (request.data.get("telephone") or "").strip()
        timezone_verbose = (request.data.get("timezone_verbose") or "").strip() or None
        if not (therapist_id is not None and date_str and number is not None):
            return Response(
                {"detail": "Indica therapist_id, date (YYYY-MM-DD) y number."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not email:
            return Response({"detail": "El email es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            therapist_id = int(therapist_id)
            number = int(number)
        except (TypeError, ValueError):
            return Response({"detail": "therapist_id y number deben ser enteros."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "date debe ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        therapist = get_object_or_404(Therapist, pk=therapist_id)
        patient = _get_or_create_patient(email, first_name, last_name, telephone, timezone_verbose)
        meet = (
            Meet.objects.select_for_update()
            .filter(therapist=therapist, date=day, number=number, status="F")
            .first()
        )
        if not meet:
            return Response(
                {"detail": "Ese turno ya no está disponible."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        meet.patient = patient
        meet.status = "D"
        meet.save()
        return Response(MeetSerializer(meet).data, status=status.HTTP_200_OK)
