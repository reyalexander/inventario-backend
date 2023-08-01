from django.shortcuts import render
from .models import Order
from .serializers import OrderSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.views import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from order_detail.models import OrderDetail


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]


class BoletaPDFView(View):
    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order_details = OrderDetail.objects.filter(id_order=order)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="boleta_{order.order_code}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)

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
        p.drawString(400, y - 60, f'Total de la Orden: {total_orden}')

        # Finalizar el PDF
        p.showPage()
        p.save()

        return response