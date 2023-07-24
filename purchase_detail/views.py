from .models import PurchaseDetail
from .serializers import PurchaseDetailSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

class PurchaseDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]