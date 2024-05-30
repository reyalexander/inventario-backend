from django.db import models
from categories.models import Category

class Product(models.Model):
    code = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=250, default='', blank=True)
    cost = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='products', blank=True, null=True)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']

    def generate_product_code(self):
        product_id = self.id
        self.code = f"PR-000{product_id:02d}"
        self.save(update_fields=['code'])

    def save(self, *args, **kwargs):
        if not self.code:   ### PR-0001
            super().save(*args, **kwargs)  # Guarda el objeto primero para obtener un ID asignado
            self.generate_product_code()  # Genera el código de parte después de que el objeto se haya guardado
        else:
            super().save(*args, **kwargs)