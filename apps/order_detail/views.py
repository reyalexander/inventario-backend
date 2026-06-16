from django.shortcuts import render
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from .models import OrderDetail, Order
from apps.products.models import Product
from .serializers import OrderDetailSerializer


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id_order']

    @transaction.atomic
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
            serializer.is_valid(raise_exception=True)

            order_details = serializer.save()
            self.update_stock_on_create(order_details)

            if order_details:
                self.update_order_totals(order_details[0].id_order.id)

            return Response(
                OrderDetailSerializer(order_details, many=True).data,
                status=status.HTTP_201_CREATED
            )

        data = dict(data)
        if 'manage_stock' not in data:
            data['manage_stock'] = False

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        order_detail = serializer.save()
        self.update_stock_on_create([order_detail])
        self.update_order_totals(order_detail.id_order.id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        old_quantity = instance.quantity or 0
        old_product = instance.id_product
        old_manage_stock = instance.manage_stock

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        new_quantity = updated_instance.quantity or 0
        new_product = updated_instance.id_product
        new_manage_stock = updated_instance.manage_stock

        # Caso 1: mismo producto -> ajustar por diferencia
        if old_product.id == new_product.id:
            diff = new_quantity - old_quantity

            if new_manage_stock:
                new_product.stock = (new_product.stock or 0) - diff
                new_product.save(update_fields=["stock"])
            else:
                if diff > 0:
                    if diff > (new_product.stock or 0):
                        raise ValidationError("La cantidad solicitada es mayor que el stock disponible.")
                    new_product.stock = (new_product.stock or 0) - diff
                elif diff < 0:
                    new_product.stock = (new_product.stock or 0) + abs(diff)

                new_product.save(update_fields=["stock"])

        else:
            # Caso 2: cambió de producto
            # devolver stock al producto viejo
            old_product.stock = (old_product.stock or 0) + old_quantity
            old_product.save(update_fields=["stock"])

            # descontar stock al producto nuevo
            if new_manage_stock:
                new_product.stock = (new_product.stock or 0) - new_quantity
            else:
                if new_quantity > (new_product.stock or 0):
                    raise ValidationError("La cantidad solicitada es mayor que el stock disponible.")
                new_product.stock = (new_product.stock or 0) - new_quantity

            new_product.save(update_fields=["stock"])

        self.update_order_totals(updated_instance.id_order.id)

        return Response(self.get_serializer(updated_instance).data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        product = instance.id_product
        quantity = instance.quantity or 0
        order_id = instance.id_order.id

        # devolver stock al eliminar detalle
        product.stock = (product.stock or 0) + quantity
        product.save(update_fields=["stock"])

        instance.delete()
        self.update_order_totals(order_id)

        return Response(status=status.HTTP_204_NO_CONTENT)

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

    def update_stock_on_create(self, order_details):
        for order_detail in order_details:
            product = Product.objects.get(id=order_detail.id_product.id)

            if order_detail.manage_stock:
                product.stock = (product.stock or 0) - (order_detail.quantity or 0)
                product.save(update_fields=["stock"])
            else:
                if (order_detail.quantity or 0) > (product.stock or 0):
                    raise ValidationError("La cantidad solicitada es mayor que el stock disponible.")
                product.stock = (product.stock or 0) - (order_detail.quantity or 0)
                product.save(update_fields=["stock"])