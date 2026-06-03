from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('products/label30x20/<int:product_id>/', ProductLabel30x20PDFView.as_view(), name='product-label-30x20'),
]