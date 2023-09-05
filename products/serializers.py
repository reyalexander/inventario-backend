from rest_framework import serializers
from products.models import Product
from categories.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id','code','name','description','cost','price','stock','product_image','created_at','updated_at','deleted','id_category','category_name']

    def get_category_name(self, obj):
        # Retorna el nombre del cliente asociado a la orden
        return obj.id_category.name if obj.id_category else None
