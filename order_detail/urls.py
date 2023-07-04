from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.OrderDetailViewSet)

urlpatterns = [
    path('order_details/', include(router.urls))
]