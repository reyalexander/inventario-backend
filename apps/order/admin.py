from django.contrib import admin
from .models import Order, CashClosure

admin.site.register(Order)
admin.site.register(CashClosure)