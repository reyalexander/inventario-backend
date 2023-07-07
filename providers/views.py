from django.shortcuts import render
from .models import Provider
from .serializers import ProviderSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'document']