from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Patient
from .serializers import (
    PatientListSerializer,
    PatientCreateSerializer,
    PatientDetailSerializer,
    PatientUpdateSerializer,
)


class PatientListAPIView(APIView):
    def get(self, request):
        qs = Patient.objects.all().select_related("user")
        serializer = PatientListSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        patient = serializer.save()
        out = PatientListSerializer(patient)
        return Response(out.data, status=status.HTTP_201_CREATED)


class PatientDetailAPIView(APIView):
    def get(self, request, pk):
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
        serializer = PatientDetailSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
        serializer = PatientUpdateSerializer(
            patient,
            data=request.data,
            partial=False,
            context={"instance": patient},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        out = PatientListSerializer(patient)
        return Response(out.data)

    def patch(self, request, pk):
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
        serializer = PatientUpdateSerializer(
            patient,
            data=request.data,
            partial=True,
            context={"instance": patient},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        out = PatientListSerializer(patient)
        return Response(out.data)

    def delete(self, request, pk):
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
        user = patient.user
        patient.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientActivateAPIView(APIView):
    def post(self, request, pk):
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
        patient.user.is_active = True
        patient.user.save()
        return Response(PatientListSerializer(patient).data)


class PatientDeactivateAPIView(APIView):
    def post(self, request, pk):
        patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
        patient.user.is_active = False
        patient.user.save()
        return Response(PatientListSerializer(patient).data)

