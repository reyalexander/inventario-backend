from django.shortcuts import render
from .models import OrderDetail
from products.models import Product
from .serializers import OrderDetailSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            serializers = [self.get_serializer(data=item) for item in data]
            valid = all(serializer.is_valid() for serializer in serializers)
            if valid:
                order_details = [serializer.save() for serializer in serializers]
                return Response(OrderDetailSerializer(order_details, many=True).data, status=status.HTTP_201_CREATED)
            else:
                errors = [serializer.errors for serializer in serializers]
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        

    def perform_create(self, serializer):
        order_detail = serializer.save()
        product = Product.objects.get(id=order_detail.id_product.id)
        if order_detail.quantity > product.stock:
            raise ValidationError("La cantidad solicitada es mayor que el stock disponible.")
        product.stock -= order_detail.quantity
        product.save()