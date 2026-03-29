import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.merchants.models import Merchant


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT, related_name='audit_logs', null=True, blank=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100, blank=True)
    before_state = models.JSONField(default=dict, blank=True)
    after_state = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} on {self.resource_type} by {self.actor}'

    @classmethod
    def log(cls, action, resource_type, resource_id='', merchant=None, actor=None,
            before_state=None, after_state=None, ip_address=None, user_agent=''):
        return cls.objects.create(
            merchant=merchant,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            before_state=before_state or {},
            after_state=after_state or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
