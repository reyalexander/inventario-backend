from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.PurchaseViewSet)

urlpatterns = [
    path('purchase/', include(router.urls))
]