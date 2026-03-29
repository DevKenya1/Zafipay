import hmac
import hashlib
import logging
import json
import requests
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from .models import WebhookEndpoint, WebhookDelivery

logger = logging.getLogger(__name__)

RETRY_DELAYS = [30, 300, 1800, 7200, 86400]


def build_signature(secret, payload_str):
    return hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()


def dispatch_webhook_for_transaction(transaction, event_type):
    endpoints = WebhookEndpoint.objects.filter(
        merchant=transaction.merchant,
        is_active=True,
        events__contains=[event_type],
    )
    for endpoint in endpoints:
        payload = {
            'event': event_type,
            'data': {
                'transaction_id': str(transaction.id),
                'internal_ref': transaction.internal_ref,
                'reference': transaction.reference,
                'provider': transaction.provider,
                'method': transaction.method,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'phone': transaction.phone,
                'provider_transaction_id': transaction.provider_transaction_id,
                'created_at': transaction.created_at.isoformat(),
                'updated_at': transaction.updated_at.isoformat(),
            },
        }
        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            transaction=transaction,
            event_type=event_type,
            payload=payload,
            attempt_number=1,
            status=WebhookDelivery.STATUS_PENDING,
        )
        deliver_webhook.delay(str(delivery.id))
        logger.info('Webhook queued: ' + str(delivery.id) + ' for ' + event_type)


@shared_task(bind=True, max_retries=5)
def deliver_webhook(self, delivery_id):
    try:
        delivery = WebhookDelivery.objects.select_related('endpoint').get(id=delivery_id)
    except WebhookDelivery.DoesNotExist:
        logger.error('WebhookDelivery not found: ' + str(delivery_id))
        return

    endpoint = delivery.endpoint
    payload_str = json.dumps(delivery.payload, default=str)
    signature = build_signature(endpoint.secret, payload_str)

    headers = {
        'Content-Type': 'application/json',
        'X-Zafipay-Signature': signature,
        'X-Zafipay-Event': delivery.event_type,
        'X-Zafipay-Delivery': str(delivery.id),
    }

    try:
        response = requests.post(
            endpoint.url,
            data=payload_str,
            headers=headers,
            timeout=10,
        )

        delivery.response_status = response.status_code
        delivery.response_body = response.text[:500]
        delivery.attempt_number = self.request.retries + 1

        if response.status_code < 300:
            delivery.status = WebhookDelivery.STATUS_SUCCESS
            delivery.delivered_at = timezone.now()
            delivery.save()
            logger.info('Webhook delivered: ' + str(delivery.id))
        else:
            raise Exception('Non-2xx response: ' + str(response.status_code))

    except Exception as exc:
        delivery.attempt_number = self.request.retries + 1
        delivery.status = WebhookDelivery.STATUS_FAILED
        delivery.save()

        retry_index = self.request.retries
        if retry_index < len(RETRY_DELAYS):
            delay = RETRY_DELAYS[retry_index]
            delivery.next_retry_at = timezone.now() + timedelta(seconds=delay)
            delivery.save(update_fields=['next_retry_at'])
            logger.warning('Webhook failed, retrying in ' + str(delay) + 's: ' + str(delivery.id))
            raise self.retry(exc=exc, countdown=delay)
        else:
            logger.error('Webhook permanently failed: ' + str(delivery.id))

