from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import ExpenseCategory, Expense
from .serializers import ExpenseCategorySerializer, ExpenseSerializer
from .services import FinancialStatisticsService


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.filter(deleted=False)
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save(update_fields=["deleted"])


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.filter(deleted=False)
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "payment_method", "expense_date", "created_by"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save(update_fields=["deleted"])


class FinancialDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        user_id = request.query_params.get("user_id")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        group_by = request.query_params.get("group_by", "month")
        selected_date = request.query_params.get("selected_date")

        data = FinancialStatisticsService.get_dashboard_data(
            year=year,
            month=month,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            group_by=group_by,
            selected_date=selected_date,
        )
        return Response(data)