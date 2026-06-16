from django.db import models
from apps.products.models import Product
from apps.purchase.models import Purchase


class PurchaseDetail(models.Model):
    id_purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        ordering = ['-id']