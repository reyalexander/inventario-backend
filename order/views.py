from django.shortcuts import render
from .models import Order
from products.models import Product
from order_detail.models import OrderDetail
from order_detail.serializers import OrderDetailSerializer
from .serializers import OrderSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
