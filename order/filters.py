from django_filters import rest_framework as filters
from datetime import datetime, timedelta
import django_filters
from order.models import Order

class OrderFilter(filters.FilterSet):
    last_days = filters.NumberFilter(method='filter_last_days')
    last_weeks = filters.NumberFilter(method='filter_last_weeks')
    last_months = filters.NumberFilter(method='filter_last_months')
    last_years = filters.NumberFilter(method='filter_last_years')
    specific_date = django_filters.DateFilter(field_name='date', lookup_expr='date')
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    id_client = filters.NumberFilter(field_name='id_client__id')

    class Meta:
        model = Order
        fields = ['specific_date']

    def filter_last_days(self, queryset, name, value):
        today = datetime.now().date()
        start_date = today - timedelta(days=int(value))
        return queryset.filter(date__gte=start_date)

    def filter_last_weeks(self, queryset, name, value):
        today = datetime.now().date()
        start_date = today - timedelta(weeks=int(value))
        return queryset.filter(date__gte=start_date)

    def filter_last_months(self, queryset, name, value):
        today = datetime.now().date()
        start_date = today - timedelta(days=int(value) * 30)  # Asumiendo que un mes tiene 30 días
        return queryset.filter(date__gte=start_date)

    def filter_last_years(self, queryset, name, value):
        today = datetime.now().date()
        start_date = today - timedelta(days=int(value) * 365)  # Asumiendo que un año tiene 365 días
        return queryset.filter(date__gte=start_date)

