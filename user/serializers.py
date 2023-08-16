from user.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name','address','phone','ruc','photo','igv','dark_mode','manage_stock']

