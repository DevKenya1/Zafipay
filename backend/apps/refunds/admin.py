from django.contrib import admin
from .models import Refund


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'merchant', 'transaction', 'amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['transaction__internal_ref', 'merchant__business_name']
