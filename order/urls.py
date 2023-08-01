from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.OrderViewSet)

urlpatterns = [
    path('orders/', include(router.urls)),
    path('orders/boleta/<int:order_id>/', views.BoletaPDFView.as_view(), name='boleta_pdf'),
]