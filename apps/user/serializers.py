from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'address',
            'phone',
            'ruc',
            'photo',
            'igv',
            'dark_mode',
            'manage_stock',
            'is_active',
            'is_staff',
            'is_admin',
            'is_superuser',
            'must_change_password',
        ]
        read_only_fields = ['is_admin', 'is_superuser']

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con este username.")
        return value

    def validate_email(self, value):
        if not value:
            return value

        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        user = User(**validated_data)

        if password:
            user.set_password(password)
            user.must_change_password = False
        else:
            user.set_password("12345678")
            user.must_change_password = True

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
            instance.must_change_password = False

        instance.save()
        return instance