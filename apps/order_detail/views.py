from django.shortcuts import render
from .models import OrderDetail, Order
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from apps.products.models import Product
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
            normalized = []
            for item in data:
                item = dict(item)
                if 'manage_stock' not in item:
                    item['manage_stock'] = False
                normalized.append(item)

            serializer = self.get_serializer(data=normalized, many=True)

            if serializer.is_valid():
                order_details = serializer.save()
                self.update_stock(order_details)
                return Response(
                    OrderDetailSerializer(order_details, many=True).data,
                    status=status.HTTP_201_CREATED
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = dict(data)
        if 'manage_stock' not in data:
            data['manage_stock'] = False

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            order_detail = serializer.save()
            self.update_stock([order_detail])
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_order_totals(self, order_id):
        order = Order.objects.get(id=order_id)

        subtotal = OrderDetail.objects.filter(
            id_order=order
        ).aggregate(
            subtotal=Sum(
                ExpressionWrapper(
                    F("quantity") * F("new_sale_price"),
                    output_field=DecimalField(max_digits=9, decimal_places=2)
                )
            )
        )["subtotal"] or 0

        discount = order.discount or 0

        if discount < 0:
            discount = 0

        if discount > subtotal:
            discount = subtotal

        order.subtotal_price = subtotal
        order.discount = discount
        order.total_price = subtotal - discount
        order.save(update_fields=["subtotal_price", "discount", "total_price", "edited"])

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