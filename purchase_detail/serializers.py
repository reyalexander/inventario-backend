from rest_framework import serializers
from purchase_detail.models import PurchaseDetail

class PurchaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = '__all__'