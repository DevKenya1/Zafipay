from django.contrib import admin
from .models import Merchant, APIKey

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'email', 'country', 'mode', 'is_active', 'created_at']
    list_filter = ['mode', 'is_active', 'country']
    search_fields = ['business_name', 'email']

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'merchant', 'prefix', 'scope', 'is_active', 'last_used_at', 'created_at']
    list_filter = ['is_active', 'scope']
    search_fields = ['name', 'merchant__business_name']
