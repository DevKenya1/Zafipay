import uuid
import secrets
import hashlib
from django.db import models
from django.contrib.auth.models import User


class Merchant(models.Model):
    MODE_TEST = 'test'
    MODE_LIVE = 'live'
    MODE_CHOICES = [(MODE_TEST, 'Test'), (MODE_LIVE, 'Live')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant')
    business_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=2, default='KE')
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=MODE_TEST)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'merchants'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.business_name} ({self.mode})'


class APIKey(models.Model):
    SCOPE_FULL = 'full'
    SCOPE_PAYMENTS_ONLY = 'payments_only'
    SCOPE_READ_ONLY = 'read_only'
    SCOPE_CHOICES = [
        (SCOPE_FULL, 'Full access'),
        (SCOPE_PAYMENTS_ONLY, 'Payments only'),
        (SCOPE_READ_ONLY, 'Read only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=20)
    key_hash = models.CharField(max_length=128)
    scope = models.CharField(max_length=30, choices=SCOPE_CHOICES, default=SCOPE_FULL)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.prefix}... ({self.merchant.business_name})'

    @classmethod
    def generate(cls, merchant, name, scope=SCOPE_FULL):
        is_test = merchant.mode == Merchant.MODE_TEST
        prefix = 'sk_test_' if is_test else 'sk_live_'
        raw_key = prefix + secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = cls.objects.create(
            merchant=merchant,
            name=name,
            prefix=prefix,
            key_hash=key_hash,
            scope=scope,
        )
        return api_key, raw_key

    def verify(self, raw_key):
        return self.key_hash == hashlib.sha256(raw_key.encode()).hexdigest()