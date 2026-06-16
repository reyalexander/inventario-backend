""" from django.core.files.base import ContentFile
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
 """

from io import BytesIO

import barcode
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile


def build_product_barcode(product):
    if not product.code:
        return

    code_value = str(product.code).strip().upper()

    buffer = BytesIO()

    options = {
        "module_width": 0.22,
        "module_height": 12.0,
        "quiet_zone": 2.0,
        "font_size": 8,
        "text_distance": 1,
        "dpi": 600,
        "write_text": True,
        "background": "white",
        "foreground": "black",
    }

    code128 = barcode.get("code128", code_value, writer=ImageWriter())
    code128.write(buffer, options=options)

    filename = f"{code_value}.png"
    product.barcode_image.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=False,
    )