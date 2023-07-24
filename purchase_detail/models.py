from django.db import models
from products.models import Product
from purchase.models import Purchase

# Create your models here.
class PurchaseDetail(models.Model):
    id_purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.TextField(null=True, default=None)
    quantity = models.IntegerField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        ordering = ['-id']