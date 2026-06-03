from django.core.files.base import ContentFile
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing


def build_product_barcode(product):
    if not product.code:
        return

    barcode_drawing = createBarcodeDrawing(
        "Code128",
        value=product.code,
        barHeight=40,
        humanReadable=True,
    )

    png_data = renderPM.drawToString(barcode_drawing, fmt="PNG")

    filename = f"{product.code}.png"
    product.barcode_image.save(
        filename,
        ContentFile(png_data),
        save=False,
    )