from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('', views.UserViewSet, basename="user")

urlpatterns = [
    path('api/', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('refresh-token/', TokenRefreshView.as_view(), name="refresh_view"),
]