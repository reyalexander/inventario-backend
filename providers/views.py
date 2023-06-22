from django.shortcuts import render
from .models import Provider
from .serializers import ProviderSerializer
from rest_framework import viewsets, permissions


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]