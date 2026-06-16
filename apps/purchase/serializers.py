from rest_framework import serializers
from .models import Purchase


class PurchaseSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="id_provider.name", read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "id_provider",
            "provider_name",
            "order_code",
            "evidence",
            "detail",
            "total_price",
            "date",
            "deleted",
        ]
        read_only_fields = ["order_code", "total_price", "date"]