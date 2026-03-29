import logging
import requests
from django.conf import settings
from .base import PaymentProvider

logger = logging.getLogger(__name__)


class FlutterwaveProvider(PaymentProvider):

    BASE_URL = 'https://api.flutterwave.com/v3'

    def __init__(self):
        self.secret_key = settings.FLUTTERWAVE_SECRET_KEY
        self.public_key = settings.FLUTTERWAVE_PUBLIC_KEY
        self.webhook_secret = settings.FLUTTERWAVE_WEBHOOK_SECRET

    def initiate_payment(self, transaction, **kwargs):
        try:
            redirect_url = kwargs.get('redirect_url', 'https://zafipay.com/payment/complete')

            payload = {
                'tx_ref': transaction.internal_ref,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'redirect_url': redirect_url,
                'customer': {
                    'email': kwargs.get('email', 'customer@zafipay.com'),
                    'phonenumber': transaction.phone,
                    'name': kwargs.get('name', 'Customer'),
                },
                'customizations': {
                    'title': 'Zafipay',
                    'description': 'Payment ' + transaction.reference,
                },
                'meta': {
                    'internal_ref': transaction.internal_ref,
                    'merchant_id': str(transaction.merchant.id),
                },
            }

            headers = {
                'Authorization': 'Bearer ' + self.secret_key,
                'Content-Type': 'application/json',
            }

            logger.info('Flutterwave payload: ' + str(payload))

            url = self.BASE_URL + '/payments'
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            logger.info('Flutterwave response status: ' + str(response.status_code))
            logger.info('Flutterwave response body: ' + response.text)

            data = response.json()

            if data.get('status') == 'success':
                return {
                    'success': True,
                    'payment_link': data['data']['link'],
                    'raw': data,
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Flutterwave payment failed'),
                    'raw': data,
                }

        except requests.exceptions.RequestException as e:
            logger.error('Flutterwave payment error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def verify_payment(self, provider_transaction_id, **kwargs):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.secret_key,
            }
            url = self.BASE_URL + '/transactions/' + str(provider_transaction_id) + '/verify'
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            tx = data.get('data', {})
            return {
                'success': tx.get('status') == 'successful',
                'status': tx.get('status'),
                'amount': tx.get('amount'),
                'currency': tx.get('currency'),
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('Flutterwave verify error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def refund(self, transaction, amount, reason='', **kwargs):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.secret_key,
                'Content-Type': 'application/json',
            }
            payload = {'amount': str(amount)}
            url = self.BASE_URL + '/transactions/' + str(transaction.provider_transaction_id) + '/refund'
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': data.get('status') == 'success',
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('Flutterwave refund error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def handle_callback(self, payload, **kwargs):
        try:
            logger.info('Flutterwave webhook received: ' + str(payload))
            event = payload.get('event', '')
            data = payload.get('data', {})

            if event == 'charge.completed':
                tx_status = data.get('status', '')
                return {
                    'success': tx_status == 'successful',
                    'transaction_id': str(data.get('id', '')),
                    'tx_ref': data.get('tx_ref', ''),
                    'amount': data.get('amount'),
                    'currency': data.get('currency'),
                    'raw': payload,
                }
            else:
                return {'success': None, 'event': event, 'raw': payload}

        except Exception as e:
            logger.error('Flutterwave callback error: ' + str(e))
            return {'success': False, 'error': str(e)}
