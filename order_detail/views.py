from django.shortcuts import render
from .models import OrderDetail
from products.models import Product
from .serializers import OrderDetailSerializer
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        order_detail = serializer.save()
        product = Product.objects.get(id=order_detail.id_product.id)
        if order_detail.quantity > product.stock:
            raise ValidationError("La cantidad solicitada es mayor que el stock disponible.")
        product.stock -= order_detail.quantity
        product.save()