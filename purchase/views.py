from .models import Purchase
from .serializers import PurchaseSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]