from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta
from .models import Purchase


class PurchaseFilter(filters.FilterSet):
    last_days = filters.NumberFilter(method="filter_last_days")
    last_weeks = filters.NumberFilter(method="filter_last_weeks")
    last_months = filters.NumberFilter(method="filter_last_months")
    last_years = filters.NumberFilter(method="filter_last_years")

    specific_date = filters.DateFilter(field_name="date", lookup_expr="date")
    start_date = filters.DateFilter(field_name="date", lookup_expr="date__gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="date__lte")
    id_provider = filters.NumberFilter(field_name="id_provider__id")

    class Meta:
        model = Purchase
        fields = [
            "specific_date",
            "start_date",
            "end_date",
            "last_days",
            "last_weeks",
            "last_months",
            "last_years",
            "id_provider",
        ]

    def filter_last_days(self, queryset, name, value):
        today = timezone.localdate()
        start = today - timedelta(days=int(value))
        return queryset.filter(date__date__gte=start)

    def filter_last_weeks(self, queryset, name, value):
        today = timezone.localdate()
        start = today - timedelta(weeks=int(value))
        return queryset.filter(date__date__gte=start)

    def filter_last_months(self, queryset, name, value):
        today = timezone.localdate()
        start = today - timedelta(days=int(value) * 30)
        return queryset.filter(date__date__gte=start)

    def filter_last_years(self, queryset, name, value):
        today = timezone.localdate()
        start = today - timedelta(days=int(value) * 365)
        return queryset.filter(date__date__gte=start)