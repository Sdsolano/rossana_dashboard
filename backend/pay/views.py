from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Pay
from .serializers import (
    PayListSerializer,
    PayCreateSerializer,
    PayDetailSerializer,
    PayUpdateSerializer,
)


class PayListAPIView(APIView):
    def get(self, request):
        qs = Pay.objects.select_related("meet__therapist__user", "meet__patient__user").all().order_by("-timestamp")
        serializer = PayListSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PayCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pay = serializer.save()
        out = PayDetailSerializer(pay)
        return Response(out.data, status=status.HTTP_201_CREATED)


class PayDetailAPIView(APIView):
    def get(self, request, pk):
        pay = get_object_or_404(Pay.objects.select_related("meet__therapist__user", "meet__patient__user"), pk=pk)
        return Response(PayDetailSerializer(pay).data)

    def put(self, request, pk):
        pay = get_object_or_404(Pay, pk=pk)
        serializer = PayUpdateSerializer(pay, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(PayDetailSerializer(pay).data)

    def patch(self, request, pk):
        pay = get_object_or_404(Pay, pk=pk)
        serializer = PayUpdateSerializer(pay, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(PayDetailSerializer(pay).data)

    def delete(self, request, pk):
        pay = get_object_or_404(Pay, pk=pk)
        pay.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PayConfirmAPIView(APIView):
    """Marca un pago como realizado."""

    def post(self, request, pk):
        pay = get_object_or_404(Pay, pk=pk)
        pay.confirm()
        return Response(PayDetailSerializer(pay).data)

