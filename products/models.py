from django.db import models

class Product(models.Model):
    code = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=500, null=False)
    description = models.CharField(max_length=50, default='', blank=True)
    cost = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='products', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']