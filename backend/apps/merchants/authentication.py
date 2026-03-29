import hashlib
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer sk_'):
            return None

        raw_key = auth_header.split(' ', 1)[1]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        try:
            api_key = APIKey.objects.select_related('merchant').get(
                key_hash=key_hash,
                is_active=True,
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')

        if api_key.expires_at and api_key.expires_at < timezone.now():
            raise AuthenticationFailed('API key has expired.')

        if not api_key.merchant.is_active:
            raise AuthenticationFailed('Merchant account is inactive.')

        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])

        return (api_key.merchant.user, api_key)