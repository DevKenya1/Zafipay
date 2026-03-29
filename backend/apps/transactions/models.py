import uuid
from django.db import models
from apps.merchants.models import Merchant


class Transaction(models.Model):
    PROVIDER_MPESA = 'mpesa'
    PROVIDER_AIRTEL = 'airtel'
    PROVIDER_STRIPE = 'stripe'
    PROVIDER_FLUTTERWAVE = 'flutterwave'
    PROVIDER_PAYPAL = 'paypal'
    PROVIDER_CHOICES = [
        (PROVIDER_MPESA, 'M-Pesa'),
        (PROVIDER_AIRTEL, 'Airtel Money'),
        (PROVIDER_STRIPE, 'Stripe'),
        (PROVIDER_FLUTTERWAVE, 'Flutterwave'),
        (PROVIDER_PAYPAL, 'PayPal'),
    ]

    METHOD_STK_PUSH = 'stk_push'
    METHOD_AIRTEL_MONEY = 'airtel_money'
    METHOD_CARD = 'card'
    METHOD_PAYPAL = 'paypal'
    METHOD_CHOICES = [
        (METHOD_STK_PUSH, 'STK Push'),
        (METHOD_AIRTEL_MONEY, 'Airtel Money'),
        (METHOD_CARD, 'Card'),
        (METHOD_PAYPAL, 'PayPal'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    VALID_TRANSITIONS = {
        STATUS_PENDING: [STATUS_PROCESSING, STATUS_FAILED],
        STATUS_PROCESSING: [STATUS_COMPLETED, STATUS_FAILED],
        STATUS_COMPLETED: [STATUS_REFUNDED],
        STATUS_FAILED: [],
        STATUS_REFUNDED: [],
    }

    WEBHOOK_EVENTS = {
        STATUS_COMPLETED: 'transaction.completed',
        STATUS_FAILED: 'transaction.failed',
        STATUS_REFUNDED: 'transaction.refunded',
        STATUS_PROCESSING: 'transaction.processing',
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT, related_name='transactions')
    reference = models.CharField(max_length=100)
    internal_ref = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    phone = models.CharField(max_length=20, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    provider_transaction_id = models.CharField(max_length=255, blank=True)
    provider_meta = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['merchant', 'status']),
            models.Index(fields=['internal_ref']),
            models.Index(fields=['provider_transaction_id']),
        ]

    def __str__(self):
        return f'{self.internal_ref} - {self.amount} {self.currency} ({self.status})'

    def transition_to(self, new_status, reason=''):
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(f'Cannot transition from {self.status} to {new_status}')
        old_status = self.status
        self.status = new_status
        if reason:
            self.failure_reason = reason
        self.save(update_fields=['status', 'failure_reason', 'updated_at'])
        TransactionEvent.objects.create(
            transaction=self,
            event_type='status.' + new_status,
            from_status=old_status,
            to_status=new_status,
        )
        event_type = self.WEBHOOK_EVENTS.get(new_status)
        if event_type:
            try:
                from apps.webhooks.tasks import dispatch_webhook_for_transaction
                dispatch_webhook_for_transaction(self, event_type)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error('Webhook dispatch error: ' + str(e))
        return self


class TransactionEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction_events'
        ordering = ['created_at']
