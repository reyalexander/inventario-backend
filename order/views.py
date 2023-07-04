from django.shortcuts import render
from .models import Order
from .serializers import OrderSerializer
from rest_framework import viewsets, permissions


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]