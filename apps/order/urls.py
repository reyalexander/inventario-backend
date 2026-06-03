from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, BoletaCuadradaPDFView, BoletaPDFView, FacturaPDFView, ReportsProductAPIView, ShowProducts, PdfCreate

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders/orders_with_total_sum/', OrderViewSet.as_view({'get': 'orders_with_total_sum'}), name='order-list-with-total-sum'),
    path('orders/boleta/<int:order_id>/', BoletaPDFView.as_view(), name='boleta_pdf'),
    path('orders/factura/<int:order_id>/', FacturaPDFView.as_view(), name='factura_pdf'),
    path('orders/boletaA4/<int:order_id>/', BoletaCuadradaPDFView.as_view(), name='boletaA4_pdf'),
    path('orders/report/', ReportsProductAPIView.post, name='report'),
    path('orders/showproducts', ShowProducts.as_view(), name='showproducts'),
    path('orders/create-pdf', PdfCreate.as_view(), name='create-pdf'),
]