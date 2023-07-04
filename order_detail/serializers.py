from rest_framework import serializers
from order_detail.models import OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'