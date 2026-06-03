from .models import User
from .serializers import UserSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(deleted=False)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_staff', 'is_admin', 'is_superuser', 'is_active']

    def create(self, request, *args, **kwargs):
        # Solo admin puede crear usuarios
        if not request.user.is_superuser and not request.user.is_admin:
            return Response(
                {"detail": "No tienes permisos para crear usuarios."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()

        # Si no se manda nada, crear como vendedor por defecto
        data.setdefault("is_staff", True)
        data.setdefault("is_admin", False)
        data.setdefault("is_superuser", False)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_superuser and not request.user.is_admin and request.user.id != instance.id:
            return Response(
                {"detail": "No tienes permisos para editar este usuario."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({
            "id": user.id,
            "is_active": user.is_active
        }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = self.get_user(request.data)
            if user:
                response.data['user_id'] = user.id
                response.data['is_superuser'] = user.is_superuser
                response.data['is_admin'] = user.is_admin
                response.data['is_staff'] = user.is_staff

        return response

    def get_user(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if not user.is_active:
            return None

        if user.check_password(password):
            return user
        return None