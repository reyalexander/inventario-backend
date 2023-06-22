from django.shortcuts import render
from .models import Product
from .serializers import ProductSerializer
from rest_framework import viewsets, permissions


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]