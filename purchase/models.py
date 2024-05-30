from django.db import models
from providers.models import Provider
from products.models import Product

# Create your models here.
class Purchase(models.Model):
    id_provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    order_code = models.CharField(max_length=150, blank=True) #purchase_code
    evidence = models.ImageField(upload_to='purchase', blank=True, null=True)
    detail = models.CharField(max_length=250, blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']

    def generate_order_code(self):
        purchase_id = self.id
        self.order_code = f"PU-00{purchase_id:03d}"
        self.save(update_fields=['order_code'])

    def save(self, *args, **kwargs):
        if not self.order_code:   ### M&M-C0033-R1-P001
            super().save(*args, **kwargs)  # Guarda el objeto primero para obtener un ID asignado
            self.generate_order_code()  # Genera el código de parte después de que el objeto se haya guardado
        else:
            super().save(*args, **kwargs)