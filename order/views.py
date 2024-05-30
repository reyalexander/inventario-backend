from .models import Order
from products.models import Product
from django.shortcuts import render
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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from reportlab.platypus import Table, TableStyle, Image
from order_detail.models import OrderDetail
from user.models import User

from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from django.template.loader import render_to_string, get_template
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Sum
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
        # Excluir los registros marcados como eliminados
        return Order.objects.filter(deleted=False)
    
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


class BoletaPDFView(View):
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