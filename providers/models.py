from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=150, null=False)
    documentType = models.IntegerField(null=True, blank=True)
    document = models.CharField(max_length=25, null=True, blank=True)
    phone = models.CharField(max_length=20, default="", blank=True)
    address = models.CharField(max_length=150, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-id']