from django.db import models

class Client(models.Model):
    class DocumentType(models.IntegerChoices):
        DNI = 1
        RUC = 2
        NO_DOCUMENT = 3

    name = models.CharField(max_length=200, null=False)
    documentType = models.IntegerField(null=True, default=3, blank=True)
    document = models.CharField(max_length=25, null=True, unique=False, blank=True)
    address = models.CharField(max_length=250, default="", blank=True)
    phone = models.CharField(max_length=25, default="", blank=True)
    mail = models.CharField(max_length=60, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']