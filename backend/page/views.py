from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Page
from .serializers import PageListSerializer, PageDetailSerializer, PageCreateUpdateSerializer


class PageListAPIView(APIView):
    def get(self, request):
        qs = Page.objects.all()
        serializer = PageListSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PageCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        page = serializer.save()
        return Response(PageDetailSerializer(page).data, status=status.HTTP_201_CREATED)


class PageDetailAPIView(APIView):
    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return Response(PageDetailSerializer(page).data)

    def put(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        serializer = PageCreateUpdateSerializer(page, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(PageDetailSerializer(page).data)

    def patch(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        serializer = PageCreateUpdateSerializer(page, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(PageDetailSerializer(page).data)

    def delete(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PagePublicDetailAPIView(APIView):
    """Obtiene una página pública por slug para uso futuro en frontend público."""

    def get(self, request, slug):
        page = get_object_or_404(Page, slug=slug, is_public=True)
        return Response(PageDetailSerializer(page).data)

