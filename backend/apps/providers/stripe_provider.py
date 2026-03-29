import logging
import stripe
from django.conf import settings
from .base import PaymentProvider

logger = logging.getLogger(__name__)


class StripeProvider(PaymentProvider):

    def __init__(self):
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        stripe.api_key = self.secret_key

    def initiate_payment(self, transaction, **kwargs):
        try:
            currency = transaction.currency.lower()
            amount_cents = int(transaction.amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'internal_ref': transaction.internal_ref,
                    'merchant_id': str(transaction.merchant.id),
                    'reference': transaction.reference,
                },
                description='Payment ' + transaction.internal_ref,
            )

            logger.info('Stripe PaymentIntent created: ' + intent.id)

            return {
                'success': True,
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
                'raw': {'id': intent.id, 'status': intent.status, 'amount': intent.amount, 'currency': intent.currency},
            }

        except stripe.StripeError as e:
            logger.error('Stripe payment error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def verify_payment(self, provider_transaction_id, **kwargs):
        try:
            intent = stripe.PaymentIntent.retrieve(provider_transaction_id)
            return {
                'success': intent.status == 'succeeded',
                'status': intent.status,
                'raw': {'id': intent.id, 'status': intent.status},
            }
        except stripe.StripeError as e:
            logger.error('Stripe verify error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def refund(self, transaction, amount, reason='', **kwargs):
        try:
            amount_cents = int(amount * 100)
            refund = stripe.Refund.create(
                payment_intent=transaction.provider_transaction_id,
                amount=amount_cents,
                reason='requested_by_customer',
            )
            logger.info('Stripe refund created: ' + refund.id)
            return {
                'success': refund.status == 'succeeded',
                'refund_id': refund.id,
                'raw': {'id': refund.id, 'status': refund.status},
            }
        except stripe.StripeError as e:
            logger.error('Stripe refund error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def handle_callback(self, payload, **kwargs):
        try:
            sig_header = kwargs.get('sig_header', '')
            if self.webhook_secret and sig_header:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, self.webhook_secret
                )
            else:
                event = payload

            event_type = event.get('type', '')
            logger.info('Stripe webhook event: ' + event_type)

            if event_type == 'payment_intent.succeeded':
                intent = event['data']['object']
                return {
                    'success': True,
                    'payment_intent_id': intent['id'],
                    'amount': intent['amount'] / 100,
                    'currency': intent['currency'].upper(),
                    'internal_ref': intent.get('metadata', {}).get('internal_ref', ''),
                    'raw': event,
                }
            elif event_type == 'payment_intent.payment_failed':
                intent = event['data']['object']
                error = intent.get('last_payment_error', {})
                return {
                    'success': False,
                    'payment_intent_id': intent['id'],
                    'error': error.get('message', 'Payment failed'),
                    'internal_ref': intent.get('metadata', {}).get('internal_ref', ''),
                    'raw': event,
                }
            else:
                return {'success': None, 'event_type': event_type, 'raw': event}

        except stripe.SignatureVerificationError as e:
            logger.error('Stripe webhook signature error: ' + str(e))
            return {'success': False, 'error': 'Invalid signature'}
        except Exception as e:
            logger.error('Stripe callback error: ' + str(e))
            return {'success': False, 'error': str(e)}
