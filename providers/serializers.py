from rest_framework import serializers
from providers.models import Provider

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'