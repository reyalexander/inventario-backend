from rest_framework import serializers
from order.models import Order
from clients.models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'date', 'edited', 'description', 'total_price', 'payment_type', 'id_client', 'client_name']

    def get_client_name(self, obj):
        # Retorna el nombre del cliente asociado a la orden
        return obj.id_client.name if obj.id_client else None

   