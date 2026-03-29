import logging
import requests
from django.conf import settings
from .base import PaymentProvider

logger = logging.getLogger(__name__)


class PayPalProvider(PaymentProvider):

    SANDBOX_BASE_URL = 'https://api-m.sandbox.paypal.com'
    LIVE_BASE_URL = 'https://api-m.paypal.com'

    def __init__(self):
        self.env = settings.PAYPAL_ENV
        self.base_url = self.SANDBOX_BASE_URL if self.env == 'sandbox' else self.LIVE_BASE_URL
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET

    def get_access_token(self):
        url = self.base_url + '/v1/oauth2/token'
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            data={'grant_type': 'client_credentials'},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()['access_token']

    def initiate_payment(self, transaction, **kwargs):
        try:
            access_token = self.get_access_token()
            return_url = kwargs.get('return_url', 'https://zafipay.com/payment/complete')
            cancel_url = kwargs.get('cancel_url', 'https://zafipay.com/payment/cancel')

            payload = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'reference_id': transaction.internal_ref,
                    'description': 'Payment ' + transaction.reference,
                    'amount': {
                        'currency_code': transaction.currency,
                        'value': str(transaction.amount),
                    },
                }],
                'application_context': {
                    'return_url': return_url,
                    'cancel_url': cancel_url,
                    'brand_name': 'Zafipay',
                    'user_action': 'PAY_NOW',
                },
            }

            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
            }

            logger.info('PayPal order payload: ' + str(payload))

            url = self.base_url + '/v2/checkout/orders'
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            logger.info('PayPal response status: ' + str(response.status_code))
            logger.info('PayPal response body: ' + response.text)

            data = response.json()

            if response.status_code == 201:
                approve_link = next(
                    (link['href'] for link in data.get('links', []) if link['rel'] == 'approve'),
                    None
                )
                return {
                    'success': True,
                    'order_id': data['id'],
                    'approve_url': approve_link,
                    'raw': data,
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'PayPal order creation failed'),
                    'raw': data,
                }

        except requests.exceptions.RequestException as e:
            logger.error('PayPal payment error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def verify_payment(self, provider_transaction_id, **kwargs):
        try:
            access_token = self.get_access_token()
            headers = {'Authorization': 'Bearer ' + access_token}
            url = self.base_url + '/v2/checkout/orders/' + provider_transaction_id
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': data.get('status') == 'COMPLETED',
                'status': data.get('status'),
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('PayPal verify error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def capture_payment(self, order_id):
        try:
            access_token = self.get_access_token()
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
            }
            url = self.base_url + '/v2/checkout/orders/' + order_id + '/capture'
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': data.get('status') == 'COMPLETED',
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('PayPal capture error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def refund(self, transaction, amount, reason='', **kwargs):
        try:
            access_token = self.get_access_token()
            capture_id = transaction.provider_meta.get('capture_id', '')
            if not capture_id:
                return {'success': False, 'error': 'No capture ID found for refund.'}
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
            }
            payload = {
                'amount': {
                    'value': str(amount),
                    'currency_code': transaction.currency,
                },
                'note_to_payer': reason or 'Refund from Zafipay',
            }
            url = self.base_url + '/v2/payments/captures/' + capture_id + '/refund'
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': data.get('status') == 'COMPLETED',
                'refund_id': data.get('id'),
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('PayPal refund error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def handle_callback(self, payload, **kwargs):
        try:
            logger.info('PayPal webhook received: ' + str(payload))
            event_type = payload.get('event_type', '')
            resource = payload.get('resource', {})

            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                return {
                    'success': True,
                    'capture_id': resource.get('id'),
                    'order_id': resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id', ''),
                    'amount': resource.get('amount', {}).get('value'),
                    'currency': resource.get('amount', {}).get('currency_code'),
                    'raw': payload,
                }
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                return {
                    'success': False,
                    'error': 'Payment capture denied',
                    'raw': payload,
                }
            else:
                return {'success': None, 'event_type': event_type, 'raw': payload}

        except Exception as e:
            logger.error('PayPal callback error: ' + str(e))
            return {'success': False, 'error': str(e)}
