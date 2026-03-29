from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'resource_type', 'resource_id', 'merchant', 'actor', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type']
    search_fields = ['action', 'resource_type', 'resource_id', 'merchant__business_name']
    readonly_fields = ['id', 'merchant', 'actor', 'action', 'resource_type', 'resource_id',
                       'before_state', 'after_state', 'ip_address', 'user_agent', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
