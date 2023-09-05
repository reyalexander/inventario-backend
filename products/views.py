from .models import Product
from .serializers import ProductSerializer
from rest_framework import viewsets, permissions,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Q


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code','description','id_category','category_name']

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search_query')
        if search_query:
            # Utilizamos Q objects para hacer una búsqueda "OR" en múltiples campos
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Búsqueda en el campo "name"
                Q(code__icontains=search_query) |  # Búsqueda en el campo "code" (si es necesario)
                Q(description__icontains=search_query)
            )
        return queryset