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
    filterset_fields = ['id_order']

    def create(self, request, *args, **kwargs):
        data = request.data
        
        if isinstance(data, list):
            for item in data:
                if 'manage_stock' not in item:
                    # Si 'manage_stock' no está en los datos, mantenemos el valor actual
                    item['manage_stock'] = False

            serializers = [self.get_serializer(data=item) for item in data]
            valid = all(serializer.is_valid() for serializer in serializers)
            
            if valid:
                order_details = [serializer.save() for serializer in serializers]
                self.update_stock(order_details)
                
                return Response(OrderDetailSerializer(order_details, many=True).data, status=status.HTTP_201_CREATED)
            else:
                errors = [serializer.errors for serializer in serializers]
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            if 'manage_stock' not in data:
                # Si 'manage_stock' no está en los datos, mantenemos el valor actual
                data['manage_stock'] = False
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                order_detail = serializer.save()
                self.update_stock([order_detail])
                
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_stock(self, order_details):
        for order_detail in order_details:
            product = Product.objects.get(id=order_detail.id_product.id)

            if order_detail.manage_stock:
                # Si manage_stock es True, reducir el stock incluso si la cantidad es mayor que el stock
                product.stock -= order_detail.quantity
                product.save()
            else:
                # Si manage_stock es False, validar si la cantidad es mayor que el stock
                if order_detail.quantity > product.stock:
                    raise ValidationError("La cantidad solicitada es mayor que el stock disponible.")
                product.stock -= order_detail.quantity
                product.save()