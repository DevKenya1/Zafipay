import logging
import requests
from django.conf import settings
from .base import PaymentProvider

logger = logging.getLogger(__name__)


class AirtelProvider(PaymentProvider):

    SANDBOX_BASE_URL = 'https://openapiuat.airtelkenya.com'
    LIVE_BASE_URL = 'https://openapi.airtelkenya.com'

    def __init__(self):
        self.env = settings.AIRTEL_ENV
        self.base_url = self.SANDBOX_BASE_URL if self.env == 'sandbox' else self.LIVE_BASE_URL
        self.client_id = settings.AIRTEL_CLIENT_ID
        self.client_secret = settings.AIRTEL_CLIENT_SECRET
        self.callback_url = settings.AIRTEL_CALLBACK_URL

    def get_access_token(self):
        url = f'{self.base_url}/auth/oauth2/token'
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()['access_token']

    def initiate_payment(self, transaction, **kwargs):
        try:
            access_token = self.get_access_token()

            phone = transaction.phone.replace('+', '').replace('-', '').strip()
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            if phone.startswith('7') or phone.startswith('1'):
                phone = '254' + phone

            payload = {
                'reference': transaction.reference[:20],
                'subscriber': {
                    'country': 'KE',
                    'currency': transaction.currency,
                    'msisdn': phone,
                },
                'transaction': {
                    'amount': int(transaction.amount),
                    'country': 'KE',
                    'currency': transaction.currency,
                    'id': transaction.internal_ref[:20],
                },
            }

            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'X-Country': 'KE',
                'X-Currency': transaction.currency,
            }

            logger.info('Airtel payment payload: ' + str(payload))

            url = f'{self.base_url}/merchant/v2/payments/'
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            logger.info('Airtel response status: ' + str(response.status_code))
            logger.info('Airtel response body: ' + response.text)

            if response.status_code == 200:
                data = response.json()
                status_code = data.get('status', {}).get('code', '')
                if status_code == '200':
                    return {
                        'success': True,
                        'airtel_money_id': data.get('data', {}).get('transaction', {}).get('id', ''),
                        'raw': data,
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('status', {}).get('message', 'Airtel payment failed'),
                        'raw': data,
                    }
            else:
                return {
                    'success': False,
                    'error': 'Airtel error ' + str(response.status_code) + ': ' + response.text,
                }

        except requests.exceptions.RequestException as e:
            logger.error('Airtel payment error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def verify_payment(self, provider_transaction_id, **kwargs):
        try:
            access_token = self.get_access_token()
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Accept': '*/*',
                'X-Country': 'KE',
                'X-Currency': 'KES',
            }
            url = f'{self.base_url}/standard/v1/payments/' + provider_transaction_id
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            tx_status = data.get('data', {}).get('transaction', {}).get('status', '')
            return {
                'success': tx_status == 'TS',
                'status': tx_status,
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('Airtel verify error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def refund(self, transaction, amount, reason='', **kwargs):
        try:
            access_token = self.get_access_token()
            payload = {
                'transaction': {
                    'airtel_money_id': transaction.provider_transaction_id,
                },
            }
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'X-Country': 'KE',
                'X-Currency': 'KES',
            }
            url = f'{self.base_url}/standard/v1/payments/refund'
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': data.get('status', {}).get('code', '') == '200',
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('Airtel refund error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def handle_callback(self, payload, **kwargs):
        try:
            logger.info('Airtel callback received: ' + str(payload))
            transaction_data = payload.get('transaction', {})
            tx_status = transaction_data.get('status_code', '')
            airtel_money_id = transaction_data.get('airtel_money_id', '')
            message = transaction_data.get('message', '')
            if tx_status == 'TS':
                return {
                    'success': True,
                    'airtel_money_id': airtel_money_id,
                    'message': message,
                    'raw': payload,
                }
            else:
                return {
                    'success': False,
                    'airtel_money_id': airtel_money_id,
                    'error': message or 'Payment failed',
                    'status_code': tx_status,
                    'raw': payload,
                }
        except Exception as e:
            logger.error('Airtel callback parse error: ' + str(e))
            return {'success': False, 'error': str(e)}
