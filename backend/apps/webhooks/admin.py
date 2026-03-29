from django.contrib import admin
from .models import WebhookEndpoint, WebhookDelivery


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'url', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['url', 'merchant__business_name']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'endpoint', 'attempt_number', 'response_status', 'status', 'created_at']
    list_filter = ['status', 'event_type']
    search_fields = ['event_type', 'endpoint__url']
