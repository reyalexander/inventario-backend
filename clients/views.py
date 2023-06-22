
from django.shortcuts import render
from .models import Client
from .serializers import ClientSerializer
from rest_framework import viewsets, permissions


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]