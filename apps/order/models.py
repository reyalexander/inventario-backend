from django.db import models
from apps.clients.models import Client
from django.conf import settings
from django.utils import timezone


class Order(models.Model):
    class PaymentType(models.IntegerChoices):
        EFECTIVO = 1, "Efectivo"
        YAPE = 2, "Yape"
        PLIN = 3, "Plin"
        TRANSFERENCIA = 4, "Transferencia"
        TARJETA = 5, "Tarjeta"

    order_code = models.CharField(max_length=150, blank=True, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)
    description = models.TextField(null=True, default=None, blank=True)

    subtotal_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    payment_type = models.IntegerField(choices=PaymentType.choices, default=PaymentType.EFECTIVO)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    canceled = models.BooleanField(default=False)
    cancel_reason = models.TextField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save(update_fields=["deleted"])

    def generate_order_code_value(self):
        return f"ORD-{self.id:05d}"

    def apply_total(self):
        subtotal = self.subtotal_price or 0
        discount = self.discount or 0

        if discount < 0:
            discount = 0

        if discount > subtotal:
            discount = subtotal

        self.discount = discount
        self.total_price = subtotal - discount

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not is_new:
            self.apply_total()

        super().save(*args, **kwargs)

        if not self.order_code:
            self.order_code = self.generate_order_code_value()
            self.apply_total()
            super().save(update_fields=["order_code", "discount", "total_price", "edited"])

    
    def cancel(self, user, reason):
        self.canceled = True
        self.cancel_reason = reason
        self.canceled_at = timezone.now()

        # Solo por seguridad: si no tiene usuario asignado, asigna quien anuló
        if not self.user:
            self.user = user

        self.save(update_fields=["canceled", "cancel_reason", "canceled_at", "user", "edited"])