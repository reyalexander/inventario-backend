from django.db import models
from .utils import build_product_barcode
from apps.categories.models import Category


class Product(models.Model):
    code = models.CharField(max_length=150, blank=True, unique=True)
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=250, default="", blank=True)
    cost = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to="products", blank=True, null=True)
    barcode_image = models.ImageField(upload_to="products/barcode/", blank=True, null=True)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ["-id"]

    def generate_product_code_value(self):
        return f"PR{self.id:05d}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        changed = False

        if not self.code:
            self.code = self.generate_product_code_value()
            changed = True

        if not self.barcode_image and self.code:
            build_product_barcode(self)
            changed = True

        if changed:
            super().save(update_fields=["code", "barcode_image", "updated_at"])