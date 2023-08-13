from rest_framework import serializers
from purchase_detail.models import PurchaseDetail
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class PurchaseDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseDetail
        fields = ['id_purchase','quantity','purchase_price','sale_price','id_product','product_name']

    def get_product_name(self, obj):
        # Retorna el nombre del cliente asociado a la orden
        return obj.id_product.name if obj.id_product else None