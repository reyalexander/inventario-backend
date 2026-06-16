from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db import transaction

from .models import Purchase
from .serializers import PurchaseSerializer
from .filters import PurchaseFilter
from apps.purchase_detail.models import PurchaseDetail


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PurchaseFilter
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Purchase.objects.filter(deleted=False).order_by("-date")

        has_filters = any([
            self.request.query_params.get("specific_date"),
            self.request.query_params.get("start_date"),
            self.request.query_params.get("end_date"),
            self.request.query_params.get("last_days"),
            self.request.query_params.get("last_weeks"),
            self.request.query_params.get("last_months"),
            self.request.query_params.get("last_years"),
            self.request.query_params.get("id_provider"),
        ])

        return queryset

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        details = PurchaseDetail.objects.select_related("id_product").filter(id_purchase=instance)

        for detail in details:
            product = detail.id_product
            qty = detail.quantity or 0

            product.stock = (product.stock or 0) - qty
            if product.stock < 0:
                product.stock = 0

            product.save(update_fields=["stock", "updated_at"])

        instance.deleted = True
        instance.save(update_fields=["deleted"])

        return Response(status=status.HTTP_204_NO_CONTENT)