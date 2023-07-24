from django.db import models
from providers.models import Provider
from products.models import Product

# Create your models here.
class Purchase(models.Model):
    id_provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    order_code = models.CharField(max_length=150, blank=True)
    evidence = models.ImageField(upload_to='purchase', blank=True, null=True)
    detail = models.CharField(max_length=250, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']