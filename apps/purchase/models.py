from django.db import models
from apps.providers.models import Provider


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

    def generate_order_code_value(self):
        return f"PU-{self.id:05d}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.order_code:
            self.order_code = self.generate_order_code_value()
            super().save(update_fields=["order_code"])