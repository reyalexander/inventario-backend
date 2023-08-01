
from django.shortcuts import render
from .models import Client
from .serializers import ClientSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'document', 'phone',]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search_query')
        if search_query:
            # Utilizamos Q objects para hacer una búsqueda "OR" en múltiples campos
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Búsqueda en el campo "name"
                Q(document__icontains=search_query) | # Búsqueda en el campo "document" (si es necesario)
                Q(phone__icontains=search_query)
            )
        return queryset