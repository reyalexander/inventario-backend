from datetime import datetime, timedelta

from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek, TruncYear
from apps.order.models import Order
from apps.order_detail.models import OrderDetail
from .models import Expense


class FinancialStatisticsService:
    @staticmethod
    def get_base_orders(user_id=None, date_from=None, date_to=None):
        qs = Order.objects.filter(deleted=False, canceled=False)

        if user_id:
            qs = qs.filter(user_id=user_id)

        if date_from:
            qs = qs.filter(date__date__gte=date_from)

        if date_to:
            qs = qs.filter(date__date__lte=date_to)

        return qs

    @staticmethod
    def get_base_expenses(user_id=None, date_from=None, date_to=None):
        qs = Expense.objects.filter(deleted=False)

        if user_id:
            qs = qs.filter(created_by_id=user_id)

        if date_from:
            qs = qs.filter(expense_date__gte=date_from)

        if date_to:
            qs = qs.filter(expense_date__lte=date_to)

        return qs

    @staticmethod
    def resolve_period_filters(group_by="month", selected_date=None, year=None, month=None):
        today = datetime.today().date()

        if selected_date:
            base_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        else:
            base_date = today

        if group_by == "day":
            return {
                "date_from": base_date,
                "date_to": base_date,
            }

        if group_by == "week":
            start_of_week = base_date - timedelta(days=base_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return {
                "date_from": start_of_week,
                "date_to": end_of_week,
            }

        if group_by == "month":
            selected_year = int(year) if year else base_date.year
            selected_month = int(month) if month else base_date.month

            start_date = datetime(selected_year, selected_month, 1).date()

            if selected_month == 12:
                end_date = datetime(selected_year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(selected_year, selected_month + 1, 1).date() - timedelta(days=1)

            return {
                "date_from": start_date,
                "date_to": end_date,
            }

        if group_by == "year":
            selected_year = int(year) if year else base_date.year
            return {
                "date_from": datetime(selected_year, 1, 1).date(),
                "date_to": datetime(selected_year, 12, 31).date(),
            }

        return {
            "date_from": None,
            "date_to": None,
        }

    @staticmethod
    def get_order_period_trunc(group_by):
        if group_by == "day":
            return TruncDay("date")
        if group_by == "week":
            return TruncDay("date")
        if group_by == "month":
            return TruncDay("date")
        if group_by == "year":
            return TruncMonth("date")
        return TruncMonth("date")

    @staticmethod
    def get_expense_period_trunc(group_by):
        if group_by == "day":
            return TruncDay("expense_date")
        if group_by == "week":
            return TruncDay("expense_date")
        if group_by == "month":
            return TruncDay("expense_date")
        if group_by == "year":
            return TruncMonth("expense_date")
        return TruncMonth("expense_date")

    @staticmethod
    def format_period(period, group_by):
        if not period:
            return ""

        if group_by == "day":
            return period.strftime("%Y-%m-%d")

        if group_by == "week":
            return period.strftime("%Y-%m-%d")

        if group_by == "month":
            return period.strftime("%Y-%m-%d")

        if group_by == "year":
            return period.strftime("%Y-%m")

        return period.strftime("%Y-%m")

    @classmethod
    def get_dashboard_data(
        cls,
        year=None,
        month=None,
        user_id=None,
        date_from=None,
        date_to=None,
        group_by="month",
        selected_date=None,
    ):
        resolved_filters = cls.resolve_period_filters(
            group_by=group_by,
            selected_date=selected_date,
            year=year,
            month=month,
        )

        if not date_from:
            date_from = resolved_filters["date_from"]

        if not date_to:
            date_to = resolved_filters["date_to"]

        orders = cls.get_base_orders(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
        expenses = cls.get_base_expenses(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )

        total_sales = orders.aggregate(total=Sum("total_price"))["total"] or 0
        total_discount = orders.aggregate(total=Sum("discount"))["total"] or 0
        total_orders = orders.count()
        avg_ticket = round((total_sales / total_orders), 2) if total_orders > 0 else 0

        total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or 0
        total_expense_count = expenses.count()
        profit_total = total_sales - total_expenses

        order_period_trunc = cls.get_order_period_trunc(group_by)
        expense_period_trunc = cls.get_expense_period_trunc(group_by)

        sales_by_period = (
            orders.annotate(period=order_period_trunc)
            .values("period")
            .annotate(
                total=Sum("total_price"),
                orders=Count("id"),
                discounts=Sum("discount"),
            )
            .order_by("period")
        )

        expenses_by_period = (
            expenses.annotate(period=expense_period_trunc)
            .values("period")
            .annotate(
                total=Sum("amount"),
                count=Count("id"),
            )
            .order_by("period")
        )

        expenses_by_category = (
            expenses.values("category_id", "category__name")
            .annotate(
                total=Sum("amount"),
                count=Count("id"),
            )
            .order_by("-total")
        )

        sales_by_vendor = (
            orders.values("user_id", "user__first_name", "user__last_name")
            .annotate(
                total_sales=Sum("total_price"),
                total_discount=Sum("discount"),
                total_orders=Count("id"),
            )
            .order_by("-total_sales")
        )

        discounts_by_vendor = (
            orders.values("user_id", "user__first_name", "user__last_name")
            .annotate(
                total_discount=Sum("discount"),
                total_orders=Count("id"),
            )
            .order_by("-total_discount")
        )

        top_products = (
            OrderDetail.objects.filter(id_order__in=orders)
            .values("id_product", "id_product__name", "id_product__code")
            .annotate(
                total_quantity=Sum("quantity"),
                total_sales=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("new_sale_price"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
            )
            .order_by("-total_quantity")[:10]
        )

        sales_by_category = (
            OrderDetail.objects.filter(id_order__in=orders)
            .values("id_product__id_category", "id_product__id_category__name")
            .annotate(
                total_quantity=Sum("quantity"),
                total_sales=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("new_sale_price"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
            )
            .order_by("-total_sales")
        )

        return {
            "meta": {
                "group_by": group_by,
                "date_from": str(date_from) if date_from else None,
                "date_to": str(date_to) if date_to else None,
                "selected_date": str(selected_date) if selected_date else None,
                "year": int(year) if year else None,
                "month": int(month) if month else None,
            },
            "kpis": {
                "total_sales": float(total_sales),
                "total_discount": float(total_discount),
                "total_orders": total_orders,
                "avg_ticket": float(avg_ticket),
                "total_expenses": float(total_expenses),
                "total_expense_count": total_expense_count,
                "profit_total": float(profit_total),
            },
            "sales_by_period": [
                {
                    "period": cls.format_period(item["period"], group_by),
                    "total": float(item["total"] or 0),
                    "orders": item["orders"] or 0,
                    "discounts": float(item["discounts"] or 0),
                }
                for item in sales_by_period
            ],
            "expenses_by_period": [
                {
                    "period": cls.format_period(item["period"], group_by),
                    "total": float(item["total"] or 0),
                    "count": item["count"] or 0,
                }
                for item in expenses_by_period
            ],
            "expenses_by_category": [
                {
                    "category_id": item["category_id"],
                    "name": item["category__name"] or "Sin categoría",
                    "total": float(item["total"] or 0),
                    "count": item["count"] or 0,
                }
                for item in expenses_by_category
            ],
            "sales_by_vendor": [
                {
                    "user_id": item["user_id"],
                    "name": f'{item["user__first_name"] or ""} {item["user__last_name"] or ""}'.strip() or "Sin usuario",
                    "total_sales": float(item["total_sales"] or 0),
                    "total_discount": float(item["total_discount"] or 0),
                    "total_orders": item["total_orders"] or 0,
                }
                for item in sales_by_vendor
            ],
            "discounts_by_vendor": [
                {
                    "user_id": item["user_id"],
                    "name": f'{item["user__first_name"] or ""} {item["user__last_name"] or ""}'.strip() or "Sin usuario",
                    "total_discount": float(item["total_discount"] or 0),
                    "total_orders": item["total_orders"] or 0,
                }
                for item in discounts_by_vendor
            ],
            "top_products": [
                {
                    "product_id": item["id_product"],
                    "name": item["id_product__name"],
                    "code": item["id_product__code"],
                    "total_quantity": item["total_quantity"] or 0,
                    "total_sales": float(item["total_sales"] or 0),
                }
                for item in top_products
            ],
            "sales_by_category": [
                {
                    "category_id": item["id_product__id_category"],
                    "name": item["id_product__id_category__name"] or "Sin categoría",
                    "total_quantity": item["total_quantity"] or 0,
                    "total_sales": float(item["total_sales"] or 0),
                }
                for item in sales_by_category
            ],
        }