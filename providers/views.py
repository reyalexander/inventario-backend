from .models import Provider
from .serializers import ProviderSerializer
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from django.db.models import Q

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'document']

    def post(self, request, format=None):
        serializer = ProviderSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search_query')
        if search_query:
            # Utilizamos Q objects para hacer una búsqueda "OR" en múltiples campos
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Búsqueda en el campo "name"
                Q(document__icontains=search_query)  # Búsqueda en el campo "document" (si es necesario)
            )
        return queryset