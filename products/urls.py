from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.ProductViewSet)

urlpatterns = [
    path('products/', include(router.urls))
]