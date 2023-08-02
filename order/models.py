from django.db import models
from clients.models import Client

# Create your models here.
class Order(models.Model):
    order_code = models.CharField(max_length=150, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)
    description = models.TextField(null=True, default=None)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
 