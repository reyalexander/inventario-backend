from rest_framework import serializers
from order_detail.models import OrderDetail
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderDetail
        fields = ['id','id_order','quantity','new_sale_price','id_product','product_name','manage_stock']
        extra_kwargs = {
            'manage_stock': {'required': False, 'default': True}
        }

    def get_product_name(self, obj):
        # Retorna el nombre del cliente asociado a la orden
        return obj.id_product.name if obj.id_product else None