from user.models import User
from user.serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        password = request.data.get('password')

        if password:
            print(password)
            hashed_password = make_password(password)
            instance.set_password(hashed_password)
            instance.save(update_fields=['password'])
            print(instance)
        
        print(hashed_password)
        user = User.objects.get(email= instance)
        print(user)
        user.set_password(hashed_password)
        user.save()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        print("y se pasa aqui no?")

        return Response(serializer.data)

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