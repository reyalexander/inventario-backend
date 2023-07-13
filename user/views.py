from user.models import User
from user.serializers import UserSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(password=make_password(serializer.validated_data['password']))


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = self.get_user(request.data)
            if user.is_superuser:
                superuser_id = user.id
                response.data['user_id'] = superuser_id

        return response

    def get_user(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
        return None