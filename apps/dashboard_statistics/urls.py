from django.urls import path
from .views import DashboardStatisticsAPIView

urlpatterns = [
    path("dashboard/", DashboardStatisticsAPIView.as_view(), name="statistics-dashboard"),
]