from django.db import models
from providers.models import Provider
from products.models import Product

# Create your models here.
class Purchase(models.Model):
    id_provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    order_code = models.CharField(max_length=150, blank=True)
    evidence = models.ImageField(upload_to='purchase', blank=True, null=True)
    detail = models.CharField(max_length=250, blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']