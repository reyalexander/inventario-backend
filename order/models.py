from django.db import models
from clients.models import Client

# Create your models here.
class Order(models.Model):
    order_code = models.CharField(max_length=150, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
 