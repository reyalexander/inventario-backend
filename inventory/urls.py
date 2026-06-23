"""
URL configuration for inventory project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include("apps.user.urls")),
    path('api/v1/categories/', include("apps.categories.urls")),
    path('api/v1/clients/', include("apps.clients.urls")),
    path('api/v1/products/', include("apps.products.urls")),
    path('api/v1/providers/', include("apps.providers.urls")),
    path('api/v1/purchase/', include("apps.purchase.urls")),
    path('api/v1/purchase_details/', include("apps.purchase_detail.urls")),
    path('api/v1/orders/', include("apps.order.urls")),
    path('api/v1/order_details/', include("apps.order_detail.urls")),
    path("api/v1/statistics/", include("apps.dashboard_statistics.urls")),
    path("api/v1/finances/", include("apps.expenses.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Swagger solo disponible si drf_yasg está instalado (no incluido en el .exe)
try:
    from rest_framework.permissions import AllowAny
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    schema_view = get_schema_view(
        openapi.Info(
            title="Inventory API",
            default_version="v1",
            description="API para hacer Documentacion de mi proyecto",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="alexandercayromamani@gmail.com"),
            license=openapi.License(name='MIT')
        ),
        public=True,
        permission_classes=[AllowAny]
    )

    urlpatterns += [
        path('swagger/', schema_view.with_ui("swagger", cache_timeout=0), name="swagger-docs"),
    ]

except ImportError:
    pass  # En el .exe compilado, Swagger no estará disponible