from rest_framework import serializers
from .models import Order
from apps.clients.models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    seller_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'date', 'edited', 'deleted','description', 'total_price', 
                  'subtotal_price', 'discount','payment_type', 'id_client', 'client_name', 'user_name', 'seller_name',
                  "canceled", "cancel_reason", "canceled_at",]
        
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return "-"

    def get_client_name(self, obj):
        # Retorna el nombre del cliente asociado a la orden
        return obj.id_client.name if obj.id_client else None

    def get_seller_name(self, obj):
        if obj.user:
            full_name = f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
            return full_name or obj.user.username
        return "-"
