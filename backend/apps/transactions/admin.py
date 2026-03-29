from django.contrib import admin
from .models import Transaction, TransactionEvent

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['internal_ref', 'merchant', 'provider', 'method', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['provider', 'method', 'status', 'currency']
    search_fields = ['internal_ref', 'reference', 'phone']

@admin.register(TransactionEvent)
class TransactionEventAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'event_type', 'from_status', 'to_status', 'created_at']
