from django.db import models
from django.conf import settings


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=250, blank=True, default="")
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoría de gasto"
        verbose_name_plural = "Categorías de gasto"

    def __str__(self):
        return self.name


class Expense(models.Model):
    class PaymentMethod(models.IntegerChoices):
        EFECTIVO = 1, "Efectivo"
        YAPE = 2, "Yape"
        PLIN = 3, "Plin"
        TRANSFERENCIA = 4, "Transferencia"
        TARJETA = 5, "Tarjeta"
        OTRO = 6, "Otro"

    description = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    payment_method = models.IntegerField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.EFECTIVO
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses_created"
    )

    evidence = models.ImageField(upload_to="expenses/", null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-expense_date", "-id"]
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"{self.description} - {self.amount}"