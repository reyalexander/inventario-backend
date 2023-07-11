from django.urls import path, include
from . import views

urlpatterns = [
    path('products/', views.ProductViewSet.as_view(), name='product-create'),
]