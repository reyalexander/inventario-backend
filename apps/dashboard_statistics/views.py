from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import StatisticsService


class DashboardStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        user_id = request.query_params.get("user_id")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        group_by = request.query_params.get("group_by", "month")
        selected_date = request.query_params.get("selected_date")

        data = StatisticsService.get_dashboard_data(
            year=year,
            month=month,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            group_by=group_by,
            selected_date=selected_date,
        )
        return Response(data)