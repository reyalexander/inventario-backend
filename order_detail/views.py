from django.shortcuts import render
from .models import OrderDetail
from .serializers import OrderDetailSerializer
from rest_framework import viewsets, permissions


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]