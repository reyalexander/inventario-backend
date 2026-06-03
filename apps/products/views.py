from .models import Product
from .serializers import ProductSerializer
from rest_framework import viewsets, permissions,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q


from io import BytesIO
from django.http import HttpResponse
from django.views import View
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Flowable, Table, TableStyle
from reportlab.graphics.barcode import code128



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code','description','id_category',]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search_query')
        if search_query:
            # Utilizamos Q objects para hacer una búsqueda "OR" en múltiples campos
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Búsqueda en el campo "name"
                Q(code__icontains=search_query) |  # Búsqueda en el campo "code" (si es necesario)
                Q(description__icontains=search_query)
            )
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by-code')
    def by_code(self, request):
        code = request.query_params.get('code', '').strip()

        if not code:
            return Response(
                {'detail': 'El código es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = Product.objects.filter(code=code, deleted=False).first()

        if not product:
            return Response(
                {'detail': 'Producto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(product)
        return Response(serializer.data)
    


class BarcodeFlowable(Flowable):
    def __init__(self, value, bar_width=0.24 * mm, bar_height=6 * mm):
        super().__init__()
        self.value = value
        self.barcode = code128.Code128(
            value,
            barWidth=bar_width,
            barHeight=bar_height,
            humanReadable=True
        )
        self.width = self.barcode.width
        self.height = self.barcode.height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.barcode.drawOn(self.canv, 0, 0)

# ProductLabel30x20PDFView
class ProductLabel30x20PDFView(View):
    def get(self, request, product_id):
        product = Product.objects.get(pk=product_id, deleted=False)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="label_{product.code}.pdf"'

        buffer = BytesIO()

        ticket_width = 30 * mm
        ticket_height = 20 * mm

        doc = SimpleDocTemplate(
            buffer,
            pagesize=(ticket_width, ticket_height),
            leftMargin=1 * mm,
            rightMargin=1 * mm,
            topMargin=1 * mm,
            bottomMargin=1 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=6.5,
            leading=7,
            alignment=TA_CENTER,
            spaceAfter=3,
        )

        """ code_style = ParagraphStyle(
            'CodeStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=5.5,
            leading=6,
            alignment=TA_CENTER,
            spaceAfter=1,
        ) """

        elements = []

        # Nombre corto o recortado
        product_name = (product.name[:22] + "...") if len(product.name) > 22 else product.name
        elements.append(Paragraph(product_name.upper(), title_style))
        #elements.append(Paragraph(product.code, code_style))

        barcode_widget = BarcodeFlowable(
            product.code,
            bar_width=0.24 * mm,
            bar_height=6 * mm
        )

        barcode_table = Table(
            [[barcode_widget]],
            colWidths=[28 * mm],  # ancho útil dentro de etiqueta de 30mm con márgenes
        )

        barcode_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        elements.append(barcode_table)

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response