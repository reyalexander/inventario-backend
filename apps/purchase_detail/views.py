from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import PurchaseDetail
from .serializers import PurchaseDetailSerializer
from apps.products.models import Product
from apps.purchase.models import Purchase


class PurchaseDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id_purchase"]

    def get_queryset(self):
        return PurchaseDetail.objects.all().order_by("-id")

    def update_purchase_totals(self, purchase_id):
        purchase = Purchase.objects.get(id=purchase_id)

        total = PurchaseDetail.objects.filter(
            id_purchase=purchase
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )["total"] or Decimal("0.00")

        purchase.total_price = total
        purchase.save(update_fields=["total_price"])

    def apply_product_changes_on_create(self, detail):
        product = detail.id_product
        qty = detail.quantity or 0

        product.stock = (product.stock or 0) + qty
        product.cost = detail.purchase_price or 0
        product.price = detail.sale_price or 0
        product.save(update_fields=["stock", "cost", "price", "updated_at"])

    def apply_product_changes_on_update(self, old_detail, new_detail):
        old_product = old_detail.id_product
        new_product = new_detail.id_product

        old_qty = old_detail.quantity or 0
        new_qty = new_detail.quantity or 0

        if old_product.id == new_product.id:
            diff = new_qty - old_qty
            new_product.stock = (new_product.stock or 0) + diff
            new_product.cost = new_detail.purchase_price or 0
            new_product.price = new_detail.sale_price or 0
            new_product.save(update_fields=["stock", "cost", "price", "updated_at"])
            return

        old_product.stock = (old_product.stock or 0) - old_qty
        if old_product.stock < 0:
            old_product.stock = 0
        old_product.save(update_fields=["stock", "updated_at"])

        new_product.stock = (new_product.stock or 0) + new_qty
        new_product.cost = new_detail.purchase_price or 0
        new_product.price = new_detail.sale_price or 0
        new_product.save(update_fields=["stock", "cost", "price", "updated_at"])

    def apply_product_changes_on_delete(self, detail):
        product = detail.id_product
        qty = detail.quantity or 0

        product.stock = (product.stock or 0) - qty
        if product.stock < 0:
            product.stock = 0

        product.save(update_fields=["stock", "updated_at"])

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data

        if isinstance(data, list):
            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            details = serializer.save()

            for detail in details:
                self.apply_product_changes_on_create(detail)

            if details:
                self.update_purchase_totals(details[0].id_purchase.id)

            return Response(
                self.get_serializer(details, many=True).data,
                status=status.HTTP_201_CREATED
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        detail = serializer.save()

        self.apply_product_changes_on_create(detail)
        self.update_purchase_totals(detail.id_purchase.id)

        return Response(
            self.get_serializer(detail).data,
            status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        old_snapshot = PurchaseDetail(
            id=instance.id,
            id_purchase=instance.id_purchase,
            id_product=instance.id_product,
            quantity=instance.quantity,
            purchase_price=instance.purchase_price,
            sale_price=instance.sale_price,
        )

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_detail = serializer.save()

        self.apply_product_changes_on_update(old_snapshot, updated_detail)
        self.update_purchase_totals(updated_detail.id_purchase.id)

        return Response(
            self.get_serializer(updated_detail).data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        purchase_id = instance.id_purchase.id

        self.apply_product_changes_on_delete(instance)
        instance.delete()
        self.update_purchase_totals(purchase_id)

        return Response(status=status.HTTP_204_NO_CONTENT)