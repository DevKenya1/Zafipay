import uuid
from django.db import models
from apps.merchants.models import Merchant
from apps.transactions.models import Transaction


class WebhookEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='webhook_endpoints')
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=255, help_text='Used to sign webhook payloads')
    events = models.JSONField(default=list, help_text='List of subscribed events')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhook_endpoints'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.merchant.business_name} -> {self.url}'


class WebhookDelivery(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='deliveries')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='webhook_deliveries')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    attempt_number = models.IntegerField(default=1)
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhook_deliveries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} to {self.endpoint.url} ({self.status})'
