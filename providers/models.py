from django.db import models

class Provider(models.Model):
    class DocumentType(models.IntegerChoices):
        DNI = 1
        RUC = 2
        NO_DOCUMENT = 3
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


    @property
    def document_type(self):
        if self.documentType == Provider.DocumentType.DNI:
            return 'DNI'
        if self.documentType == Provider.DocumentType.RUC:
            return 'RUC'
        if self.documentType == Provider.DocumentType.NO_DOCUMENT:
            return 'SIN DOCUMENTO'

    def save(self, *args, **kwargs):
        if self.document == '' or self.document is None:
            self.documentType = 3
        return super(Provider, self).save(*args, **kwargs)