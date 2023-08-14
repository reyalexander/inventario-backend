from django.db import models
from products.models import Product
from order.models import Order

# Create your models here.
class OrderDetail(models.Model):
    id_order = models.ForeignKey(Order, on_delete=models.CASCADE)
    id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    new_sale_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    manage_stock = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']
 