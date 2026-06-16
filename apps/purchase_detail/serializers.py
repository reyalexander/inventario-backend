from rest_framework import serializers
from .models import PurchaseDetail


class PurchaseDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="id_product.name", read_only=True)
    product_code = serializers.CharField(source="id_product.code", read_only=True)
    product_stock = serializers.IntegerField(source="id_product.stock", read_only=True)

    class Meta:
        model = PurchaseDetail
        fields = [
            "id",
            "id_purchase",
            "id_product",
            "product_name",
            "product_code",
            "product_stock",
            "quantity",
            "purchase_price",
            "sale_price",
        ]

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value

    def validate_purchase_price(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError("El precio de compra no puede ser negativo.")
        return value

    def validate_sale_price(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError("El precio de venta no puede ser negativo.")
        return value