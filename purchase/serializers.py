from rest_framework import serializers
from purchase.models import Purchase
from providers.models import Provider

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    provider_name = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = ['id', 'order_code', 'evidence', 'detail', 'date', 'deleted', 'id_provider', 'provider_name']

    def get_provider_name(self, obj):
        # Retorna el nombre del proveedor asociado a la compra
        return obj.id_provider.name if obj.id_provider else None