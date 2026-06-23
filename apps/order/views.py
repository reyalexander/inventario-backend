from .models import Order, CashClosure
from apps.products.models import Product
from django.shortcuts import render
from django.utils import timezone
from .serializers import OrderSerializer
from .filters import OrderFilter
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.views import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from reportlab.platypus import Table, TableStyle, Image
from apps.order_detail.models import OrderDetail
from apps.user.models import User

from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm

from xhtml2pdf import pisa
from django.template.loader import render_to_string, get_template
from django.db import transaction

from django.db.models import Sum, Count
from decimal import Decimal
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # El número de elementos por página
    page_size_query_param = 'page_size'  # Parámetro para especificar el tamaño de página en la URL
    max_page_size = 1000  # Tamaño máximo de página

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total de elementos en la consulta
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = CustomPageNumberPagination    

    def get_queryset(self):
        queryset = Order.objects.filter(deleted=False).order_by("-date")

        if self.action in ["retrieve", "update", "partial_update", "destroy", "cancel_order"]:
            return queryset

        has_filters = any([
            self.request.query_params.get("specific_date"),
            self.request.query_params.get("start_date"),
            self.request.query_params.get("end_date"),
            self.request.query_params.get("last_days"),
            self.request.query_params.get("last_weeks"),
            self.request.query_params.get("last_months"),
            self.request.query_params.get("last_years"),
            self.request.query_params.get("id_client"),
        ])

        if not has_filters:
            today = timezone.localdate()
            queryset = queryset.filter(date__date=today)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def orders_with_total_sum(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        total_sum = queryset.aggregate(total_sum=Sum('total_price'))['total_sum']

        # Accede al atributo 'count' del paginador
        total_items = queryset.count()

        # Pagina los resultados automáticamente
        page = self.paginator.paginate_queryset(queryset, request=request)


        serializer = OrderSerializer(queryset, many=True)
        response_data = {
            'counts': total_items,
            'total_sum': total_sum,
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
            'results':serializer.data
        }
        return Response(response_data)
    
    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        order = self.get_object()

        if order.canceled:
            return Response({"detail": "La orden ya está anulada."}, status=400)

        reason = request.data.get("reason", "").strip()

        if not reason:
            return Response({"detail": "Debe ingresar una razón de anulación."}, status=400)

        if order.user and order.user != request.user and not (request.user.is_admin or request.user.is_superuser):
            return Response({"detail": "Solo puede anular la orden el usuario que la creó."}, status=403)

        try:
            with transaction.atomic():
                order_details = OrderDetail.objects.select_related("id_product").filter(id_order=order)

                for detail in order_details:
                    product = detail.id_product

                    # devolver stock vendido
                    product.stock = (product.stock or 0) + (detail.quantity or 0)
                    product.save(update_fields=["stock"])

                order.cancel(user=request.user, reason=reason)

            serializer = self.get_serializer(order)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"detail": f"No se pudo anular la orden: {str(e)}"},
                status=500
            )

    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_superuser):
            return Response(
                {"detail": "Solo el administrador puede eliminar órdenes."},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()

        try:
            with transaction.atomic():
                if not order.canceled:
                    order_details = OrderDetail.objects.select_related("id_product").filter(id_order=order)

                    for detail in order_details:
                        product = detail.id_product
                        product.stock = (product.stock or 0) + (detail.quantity or 0)
                        product.save(update_fields=["stock"])

                order.deleted = True
                order.save(update_fields=["deleted", "edited"])

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"detail": f"No se pudo eliminar la orden: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_daily_cash_summary(self, user, target_date):
        orders = Order.objects.filter(
            deleted=False,
            canceled=False,
            user=user,
            date__date=target_date
        )

        payment_map = {
            1: "Efectivo",
            2: "Yape",
            3: "Plin",
            4: "Transferencia",
            5: "Tarjeta",
        }

        grouped = (
            orders.values("payment_type")
            .annotate(
                total=Sum("total_price"),
                count=Count("id")
            )
            .order_by("payment_type")
        )

        grouped_dict = {item["payment_type"]: item for item in grouped}

        items = []
        total_general = Decimal("0.00")
        total_sales_count = 0

        totals_by_payment = {
            1: Decimal("0.00"),
            2: Decimal("0.00"),
            3: Decimal("0.00"),
            4: Decimal("0.00"),
            5: Decimal("0.00"),
        }

        for payment_id, payment_name in payment_map.items():
            item = grouped_dict.get(payment_id, {})
            total = Decimal(str(item.get("total") or 0))
            count = int(item.get("count") or 0)

            totals_by_payment[payment_id] = total
            total_general += total
            total_sales_count += count

            items.append({
                "payment_type": payment_id,
                "payment_name": payment_name,
                "count": count,
                "total": float(total),
            })

        return {
            "items": items,
            "total_general": total_general,
            "total_sales_count": total_sales_count,
            "expected_cash": totals_by_payment[1],
            "expected_yape": totals_by_payment[2],
            "expected_plin": totals_by_payment[3],
            "expected_transfer": totals_by_payment[4],
            "expected_card": totals_by_payment[5],
        }

    @action(detail=False, methods=["get"], url_path="daily-cash-report")
    def daily_cash_report(self, request):
        date_str = request.query_params.get("date")
        target_date = timezone.localdate()

        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "La fecha debe tener formato YYYY-MM-DD."},
                    status=400
                )

        summary = self._build_daily_cash_summary(request.user, target_date)

        closure = CashClosure.objects.filter(
            user=request.user,
            closure_date=target_date
        ).first()

        closure_data = None
        if closure:
            closure_data = {
                "id": closure.id,
                "closure_date": closure.closure_date.strftime("%Y-%m-%d"),
                "expected_cash": float(closure.expected_cash or 0),
                "expected_yape": float(closure.expected_yape or 0),
                "expected_plin": float(closure.expected_plin or 0),
                "expected_transfer": float(closure.expected_transfer or 0),
                "expected_card": float(closure.expected_card or 0),
                "total_expected": float(closure.total_expected or 0),
                "counted_cash": float(closure.counted_cash or 0),
                "cash_difference": float(closure.cash_difference or 0),
                "note": closure.note or "",
                "closed_at": timezone.localtime(closure.closed_at).strftime("%d/%m/%Y %H:%M:%S"),
            }

        return Response({
            "date": target_date.strftime("%Y-%m-%d"),
            "user_id": request.user.id,
            "user_name": (
                f"{request.user.first_name or ''} {request.user.last_name or ''}".strip()
                or getattr(request.user, "username", "")
                or "Usuario"
            ),
            "total_sales_count": summary["total_sales_count"],
            "total_general": float(summary["total_general"]),
            "items": summary["items"],
            "expected_cash": float(summary["expected_cash"]),
            "expected_yape": float(summary["expected_yape"]),
            "expected_plin": float(summary["expected_plin"]),
            "expected_transfer": float(summary["expected_transfer"]),
            "expected_card": float(summary["expected_card"]),
            "closure": closure_data,
        })

    @action(detail=False, methods=["post"], url_path="daily-cash-closure")
    def daily_cash_closure(self, request):
        date_str = request.data.get("date")
        target_date = timezone.localdate()

        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "La fecha debe tener formato YYYY-MM-DD."},
                    status=400
                )

        counted_cash = request.data.get("counted_cash", 0)
        note = str(request.data.get("note", "") or "").strip()

        try:
            counted_cash = Decimal(str(counted_cash or 0))
        except Exception:
            return Response(
                {"detail": "El efectivo contado no es válido."},
                status=400
            )

        if counted_cash < 0:
            return Response(
                {"detail": "El efectivo contado no puede ser negativo."},
                status=400
            )

        summary = self._build_daily_cash_summary(request.user, target_date)

        expected_cash = summary["expected_cash"]
        expected_yape = summary["expected_yape"]
        expected_plin = summary["expected_plin"]
        expected_transfer = summary["expected_transfer"]
        expected_card = summary["expected_card"]
        total_expected = summary["total_general"]

        cash_difference = counted_cash - expected_cash

        closure, _created = CashClosure.objects.update_or_create(
            user=request.user,
            closure_date=target_date,
            defaults={
                "expected_cash": expected_cash,
                "expected_yape": expected_yape,
                "expected_plin": expected_plin,
                "expected_transfer": expected_transfer,
                "expected_card": expected_card,
                "total_expected": total_expected,
                "counted_cash": counted_cash,
                "cash_difference": cash_difference,
                "note": note,
            }
        )

        return Response({
            "id": closure.id,
            "date": closure.closure_date.strftime("%Y-%m-%d"),
            "expected_cash": float(closure.expected_cash),
            "expected_yape": float(closure.expected_yape),
            "expected_plin": float(closure.expected_plin),
            "expected_transfer": float(closure.expected_transfer),
            "expected_card": float(closure.expected_card),
            "total_expected": float(closure.total_expected),
            "counted_cash": float(closure.counted_cash),
            "cash_difference": float(closure.cash_difference),
            "note": closure.note or "",
            "closed_at": timezone.localtime(closure.closed_at).strftime("%d/%m/%Y %H:%M:%S"),
        }, status=200)


############################################

class BoletaPDFView(View):
    def get_seller_name(self, order):
        seller = getattr(order, "user", None)
        if not seller:
            return "-"

        full_name = f"{seller.first_name or ''} {seller.last_name or ''}".strip()
        return full_name or getattr(seller, "username", "") or "-"

    def get(self, request, order_id):
        order = Order.objects.select_related("user", "id_client").get(pk=order_id)
        order_details = OrderDetail.objects.filter(id_order=order)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="boleta_{order.order_code}.pdf"'

        buffer = BytesIO()

        # Tamaño ticket térmico 80mm
        ticket_width = 80 * mm

        # Altura dinámica aproximada según cantidad de items
        base_height = 120 * mm
        extra_height = max(len(order_details), 1) * 8 * mm
        ticket_height = base_height + extra_height

        doc = SimpleDocTemplate(
            buffer,
            pagesize=(ticket_width, ticket_height),
            leftMargin=2 * mm,
            rightMargin=2 * mm,
            topMargin=2 * mm,
            bottomMargin=2 * mm,
        )

        elements = []

        # Usuario / empresa
        try:
            user = User.objects.get(id=1)
            company_image = user.photo if user.photo else None
        except User.DoesNotExist:
            user = None
            company_image = None

        # Estilos
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TicketTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=3,
        )

        normal_center = ParagraphStyle(
            'NormalCenter',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=10,
            alignment=TA_CENTER,
            spaceAfter=2,
        )

        normal_left = ParagraphStyle(
            'NormalLeft',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=10,
            alignment=TA_LEFT,
            spaceAfter=2,
        )

        small_left = ParagraphStyle(
            'SmallLeft',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9,
            alignment=TA_LEFT,
            spaceAfter=1,
        )

        total_style = ParagraphStyle(
            'TotalStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            alignment=TA_RIGHT,
            spaceBefore=4,
        )

        # Logo
        if company_image:
            try:
                image = Image(company_image.path, width=30 * mm, height=30 * mm)
                image.hAlign = 'CENTER'
                elements.append(image)
                elements.append(Spacer(1, 2 * mm))
            except Exception:
                pass

        # Cabecera empresa
        if user:
            #full_name = f"{(user.first_name or '').upper()} {(user.last_name or '').upper()}".strip()
            #if full_name:
            #    elements.append(Paragraph(full_name, title_style))

            if getattr(user, 'address', None):
                elements.append(Paragraph(user.address.upper(), normal_center))

            if getattr(user, 'phone', None):
                elements.append(Paragraph(f"Cel: {user.phone}", normal_center))

            if getattr(user, 'ruc', None):
                elements.append(Paragraph(f"RUC: {user.ruc}", normal_center))

        elements.append(Paragraph("BOLETA DE VENTA", title_style))
        elements.append(Paragraph(f"Nro: {order.order_code}", normal_center))
        elements.append(Spacer(1, 2 * mm))

        # Datos cliente
        elements.append(Paragraph(f"<b>Cliente:</b> {order.id_client.name}", normal_left))

        local_order_date = timezone.localtime(order.date)
        
        elements.append(Paragraph(f"<b>Fecha:</b> {local_order_date.strftime('%d/%m/%Y %H:%M:%S')}", normal_left))
        if getattr(order.id_client, 'document', None):
            elements.append(Paragraph(f"<b>Doc:</b> {order.id_client.document}", normal_left))

        if getattr(order.id_client, 'address', None):
            elements.append(Paragraph(f"<b>Dir:</b> {order.id_client.address}", small_left))
        
        # Datos vendedor
        elements.append(Paragraph(f"<b>Vendedor:</b> {self.get_seller_name(order)}", normal_left))

        elements.append(Spacer(1, 2 * mm))

        # Tabla productos
        table_data = [
            ['Producto', 'Cant', 'Subt.']
        ]

        total_orden = 0

        for detail in order_details:
            product = detail.id_product.name
            quantity = detail.quantity
            subtotal = detail.quantity * detail.new_sale_price
            total_orden += subtotal

            table_data.append([
                Paragraph(product, small_left),
                Paragraph(str(quantity), normal_center),
                Paragraph(f"{subtotal:.2f}", normal_center),
            ])

        usable_width = ticket_width - (8 * mm)  # restando márgenes
        table = Table(
            table_data,
            colWidths=[usable_width * 0.58, usable_width * 0.14, usable_width * 0.28],
            repeatRows=1,
            hAlign='LEFT'
        )

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black),
            ('LINEBELOW', (0, 1), (-1, -1), 0.2, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 3 * mm))

        # Totales
        discount = order.discount or 0
        final_total = order.total_price if order.total_price is not None else (total_orden - discount)

        elements.append(Paragraph(f"SubTotal: S/. {total_orden:.2f}", total_style))
        elements.append(Paragraph(f"Dcto: S/. {discount:.2f}", total_style))
        elements.append(Paragraph(f"Total: S/. {final_total:.2f}", total_style))
        elements.append(Spacer(1, 3 * mm))

        # Pie
        elements.append(Paragraph("Gracias por su compra", normal_center))

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        response.write(pdf)
        return response

""" class BoletaPDFView(View): 
    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order_details = OrderDetail.objects.filter(id_order=order)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="boleta_{order.order_code}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)

        # Obtener la imagen de la empresa y mostrarla en la cabecera de la boleta
        try:
            user = User.objects.get(id=1)  # Reemplaza '1' con el ID de la empresa o la forma en que obtienes el usuario/empresa correcto
            company_image = user.photo
            if company_image:
                p.drawImage(company_image.path, 350, 650, width=170, height=90)  # Ajusta las coordenadas según el diseño deseado
        except User.DoesNotExist:
            pass

        # Configurar los detalles de la boleta
        p.drawString(100, 700, f'Boleta de Orden #{order.order_code}')
        p.drawString(100, 680, f'Cliente: {order.id_client.name}')
        p.drawString(100, 660, f'Fecha: {order.date.strftime("%d/%m/%Y %H:%M:%S")}')

        y = 600
        p.drawString(100, y, f'PRODUCTO')
        p.drawRightString(310, y, f'CANT.')
        p.drawRightString(430, y, F'P. UNIT')
        p.drawRightString(520, y, 'SUBTOTAL')

        y = 580
        total_por_producto = 0  # Variable para almacenar el total por producto
        for order_detail in order_details:
            # Mostrar los detalles del producto en una misma línea
            producto = f'{order_detail.id_product.name}'
            cantidad = f'{order_detail.quantity}'
            precio_unitario = f'{order_detail.new_sale_price}'
            subtotal = f'{order_detail.quantity * order_detail.new_sale_price}'
            p.drawString(100, y, producto)
            p.drawRightString(300, y, cantidad) 
            p.drawRightString(420, y, precio_unitario)
            p.drawRightString(510, y, subtotal)
            p.drawString(100, y - 20, f'----------------------------------------------------------------------------------------------------------------------------')
            y -= 40

            # Si se alcanza el final de la página, crear una nueva página
            if y <= 140:
                p.showPage()
                p.drawString(100, 700, f'Boleta de Orden #{order.order_code}')
                p.drawString(100, 680, f'Cliente: {order.id_client.name}')
                p.drawString(100, 660, f'Fecha: {order.date.strftime("%d/%m/%Y %H:%M:%S")}')
                y = 620

            total_por_producto += order_detail.quantity * order_detail.new_sale_price
        # Calcular el total de la orden
        total_orden = sum(order_detail.quantity * order_detail.new_sale_price for order_detail in order_details)

        # Mostrar el total de la orden en la parte inferior de la boleta
        p.drawString(400, y - 60, f'Total de la Orden: S/. {total_orden}')

        # Finalizar el PDF
        p.showPage()
        p.save()

        return response
"""

class FacturaPDFView(View):
    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order_details = OrderDetail.objects.filter(id_order=order)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="factura_{order.order_code}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)

        # Obtener la imagen de la empresa y mostrarla en la cabecera de la boleta
        try:
            user = User.objects.get(id=1)  # Reemplaza '1' con el ID de la empresa o la forma en que obtienes el usuario/empresa correcto
            company_image = user.photo
            if company_image:
                p.drawImage(company_image.path, 400, 640, width=160, height=80)  # Ajusta las coordenadas según el diseño deseado
        except User.DoesNotExist:
            pass

        # Configurar los detalles de la boleta
        p.drawString(130, 700, user.first_name.upper() + " " + user.last_name.upper())
        p.drawString(130, 680, user.address.upper())
        p.drawString(130, 660, f'Cel.: {user.phone}')
        p.drawString(130, 640, f'RUC.: {user.ruc}')
        p.drawString(130, 620, f'FACTURA DE VENTA ELECTRÓNICA No.: {order.order_code}')

        p.drawString(80, 590, f'Sr(A): {order.id_client.name}')
        p.drawString(80, 575, f'DNI/RUC: {order.id_client.document}')
        p.drawString(80, 560, f'Dirección: {order.id_client.address.upper()}')
        p.drawString(80, 545, f'Fecha: {order.date.strftime("%d/%m/%Y %H:%M:%S")}')
        p.drawString(80, 530, f'Forma de Pago: {order.id_client.document}')

        y = 500
        p.drawString(100, y, f'PRODUCTO')
        p.drawRightString(310, y, f'CANT.')
        p.drawRightString(430, y, F'P. UNIT')
        p.drawRightString(520, y, 'SUBTOTAL')

        y = 480
        total_por_producto = 0  # Variable para almacenar el total por producto
        for order_detail in order_details:
            # Mostrar los detalles del producto en una misma línea
            producto = f'{order_detail.id_product.name}'
            cantidad = f'{order_detail.quantity}'
            precio_unitario = f'{order_detail.new_sale_price}'
            subtotal = f'{order_detail.quantity * order_detail.new_sale_price}'
            p.drawString(100, y, producto)
            p.drawRightString(300, y, cantidad) 
            p.drawRightString(420, y, precio_unitario)
            p.drawRightString(510, y, subtotal)
            p.drawString(80, y - 10, f'----------------------------------------------------------------------------------------------------------------------------')
            y -= 30

            # Si se alcanza el final de la página, crear una nueva página
            if y <= 140:
                p.showPage()
                p.drawString(100, 700, f'FACTURA DE VENTA ELECTRÓNICA No.:{order.order_code}')
                p.drawString(100, 680, f'Sr(A).: {order.id_client.name}')
                p.drawString(100, 660, f'Fecha Emi.: {order.date.strftime("%d/%m/%Y %H:%M:%S")}')
                y = 620

            total_por_producto += order_detail.quantity * order_detail.new_sale_price
        # Calcular el total de la orden
        total_orden = sum(order_detail.quantity * order_detail.new_sale_price for order_detail in order_details)

        # Mostrar el total de la orden en la parte inferior de la boleta
        p.drawString(400, y - 60, f'Total de la Orden: S/. {total_orden}')

        # Finalizar el PDF
        p.showPage()
        p.save()

        return response

class BoletaCuadradaPDFView(View):
    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order_details = OrderDetail.objects.filter(id_order=order)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="boleta_{order.order_code}.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Obtener la imagen de la empresa y mostrarla en la cabecera de la boleta
        try:
            user = User.objects.get(id=1)  # Reemplaza '1' con el ID de la empresa o la forma en que obtienes el usuario/empresa correcto
            company_image = user.photo
        except User.DoesNotExist:
            company_image = None

        # Crear la lista de elementos para la cabecera
        elements = []

        if company_image:
            image_width, image_height = 170, 100
            company_image_path = company_image.path
            image = Image(company_image_path, width=image_width, height=image_height)
            elements.append(image)

        styles = getSampleStyleSheet()
        elements.append(Paragraph(f'<b>Cliente:</b> {order.id_client.name}', styles['Normal']))
        elements.append(Paragraph(f'<b>Número de Boleta:</b> {order.order_code}', styles['Normal']))
        elements.append(Paragraph(f'<b>Fecha:</b> {order.date.strftime("%d/%m/%Y %H:%M:%S")}', styles['Normal']))
        elements.append(Spacer(1, 20))  # Espacio en blanco

        # Crear una tabla para mostrar los detalles del pedido
        table_data = [
            ['Producto', 'Cantidad', 'Subtotal'],
        ]

        for detail in order_details:
            product = detail.id_product.name
            quantity = str(detail.quantity)
            subtotal = str(detail.quantity * detail.new_sale_price)
            table_data.append([product, quantity, subtotal])

        table = Table(table_data, colWidths=[200, 100, 100], hAlign='LEFT', repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

        # Construir el documento y guardar en el buffer
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        # Devolver el PDF como respuesta
        response.write(pdf)
        return response
    


class ReportsProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.render_to_pdf(request)

    def render_to_pdf(self, request):
        
        template_path = 'products_report.html'

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Report.pdf"'

        data = {
            'filename': "REPORTE-PRODUCTOS",
            'products': "serializedProducts",
            'reportDate': datetime.now(),
            'total': "1200"
        }
        html = render_to_string(template_path, data)

        pisaStatus = pisa.CreatePDF(html, dest=response)

        return response
    
class ShowProducts(View):
    permission_classes = [permissions.AllowAny]
    def show_products(request):

        
        products = Product.objects.all()

        context = {
            'products': products
        }

        return render(request, 'showInfo.html', context)


class PdfCreate(View):
    permission_classes = [IsAuthenticated]
    def pdf_report_create(request):

        products = Product.objects.all()

        template_path = 'pdfReport.html'

        context = {'products': products}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = 'filename="products_report.pdf"'

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
