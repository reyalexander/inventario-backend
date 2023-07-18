from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

router = DefaultRouter()
router.register('', UserViewSet, basename="user")

urlpatterns = [
    path('api/', include(router.urls)),
    path('token/', CustomTokenObtainPairView .as_view(), name='get_token'),
    path('refresh-token/', TokenRefreshView.as_view(), name="refresh_view"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)