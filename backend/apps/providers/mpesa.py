import base64
import logging
import requests
from datetime import datetime
from django.conf import settings
from .base import PaymentProvider

logger = logging.getLogger(__name__)


class MpesaProvider(PaymentProvider):

    SANDBOX_BASE_URL = 'https://sandbox.safaricom.co.ke'
    LIVE_BASE_URL = 'https://api.safaricom.co.ke'

    def __init__(self):
        self.env = settings.MPESA_ENV
        self.base_url = self.SANDBOX_BASE_URL if self.env == 'sandbox' else self.LIVE_BASE_URL
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL

    def get_access_token(self):
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret), timeout=30)
        response.raise_for_status()
        return response.json()['access_token']

    def get_password(self, timestamp):
        raw = f'{self.shortcode}{self.passkey}{timestamp}'
        return base64.b64encode(raw.encode()).decode()

    def get_timestamp(self):
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def initiate_payment(self, transaction, **kwargs):
        try:
            access_token = self.get_access_token()
            timestamp = self.get_timestamp()
            password = self.get_password(timestamp)
            phone = transaction.phone.replace('+', '').replace('-', '').strip()
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            if phone.startswith('7') or phone.startswith('1'):
                phone = '254' + phone
            payload = {
                'BusinessShortCode': self.shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(transaction.amount),
                'PartyA': phone,
                'PartyB': self.shortcode,
                'PhoneNumber': phone,
                'CallBackURL': self.callback_url,
                'AccountReference': transaction.reference[:12],
                'TransactionDesc': 'Payment ' + transaction.internal_ref[:20],
            }
            logger.info('STK push payload: ' + str(payload))
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
            }
            url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            logger.info('Daraja status: ' + str(response.status_code))
            logger.info('Daraja body: ' + response.text)
            if response.status_code == 200:
                data = response.json()
                if data.get('ResponseCode') == '0':
                    return {
                        'success': True,
                        'checkout_request_id': data.get('CheckoutRequestID'),
                        'merchant_request_id': data.get('MerchantRequestID'),
                        'raw': data,
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('errorMessage', data.get('ResponseDescription', 'STK push failed')),
                        'raw': data,
                    }
            else:
                return {
                    'success': False,
                    'error': 'Daraja error ' + str(response.status_code) + ': ' + response.text,
                }
        except requests.exceptions.RequestException as e:
            logger.error('M-Pesa STK push error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def verify_payment(self, provider_transaction_id, **kwargs):
        try:
            access_token = self.get_access_token()
            timestamp = self.get_timestamp()
            password = self.get_password(timestamp)
            payload = {
                'BusinessShortCode': self.shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': provider_transaction_id,
            }
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
            }
            url = f'{self.base_url}/mpesa/stkpushquery/v1/query'
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            result_code = data.get('ResultCode')
            return {
                'success': result_code == '0' or result_code == 0,
                'result_code': result_code,
                'result_desc': data.get('ResultDesc'),
                'raw': data,
            }
        except requests.exceptions.RequestException as e:
            logger.error('M-Pesa verify error: ' + str(e))
            return {'success': False, 'error': str(e)}

    def refund(self, transaction, amount, reason='', **kwargs):
        return {'success': False, 'error': 'M-Pesa refunds not supported via API.'}

    def handle_callback(self, payload, **kwargs):
        try:
            stk_callback = payload.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            merchant_request_id = stk_callback.get('MerchantRequestID')
            if result_code == 0:
                items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                meta = {item['Name']: item.get('Value') for item in items}
                return {
                    'success': True,
                    'checkout_request_id': checkout_request_id,
                    'merchant_request_id': merchant_request_id,
                    'mpesa_receipt': meta.get('MpesaReceiptNumber'),
                    'amount': meta.get('Amount'),
                    'phone': str(meta.get('PhoneNumber', '')),
                    'transaction_date': str(meta.get('TransactionDate', '')),
                    'raw': payload,
                }
            else:
                return {
                    'success': False,
                    'checkout_request_id': checkout_request_id,
                    'error': result_desc,
                    'result_code': result_code,
                    'raw': payload,
                }
        except Exception as e:
            logger.error('M-Pesa callback parse error: ' + str(e))
            return {'success': False, 'error': str(e)}
