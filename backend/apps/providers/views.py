import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.transactions.models import Transaction
from .mpesa import MpesaProvider
from .airtel import AirtelProvider
from .stripe_provider import StripeProvider
from .flutterwave import FlutterwaveProvider
from .paypal import PayPalProvider

logger = logging.getLogger(__name__)


class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            provider = MpesaProvider()
            result = provider.handle_callback(request.data)
            checkout_request_id = result.get('checkout_request_id')
            if not checkout_request_id:
                return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})
            try:
                transaction = Transaction.objects.get(provider_transaction_id=checkout_request_id)
            except Transaction.DoesNotExist:
                logger.warning('Transaction not found: ' + str(checkout_request_id))
                return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})
            if result.get('success'):
                transaction.provider_meta.update({
                    'mpesa_receipt': result.get('mpesa_receipt'),
                    'transaction_date': result.get('transaction_date'),
                })
                transaction.save(update_fields=['provider_meta'])
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_COMPLETED)
            else:
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_FAILED, reason=result.get('error', 'Payment cancelled'))
            return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        except Exception as e:
            logger.error('Mpesa callback error: ' + str(e))
            return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})


class AirtelCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            provider = AirtelProvider()
            result = provider.handle_callback(request.data)
            airtel_money_id = result.get('airtel_money_id')
            if not airtel_money_id:
                return Response({'status': 'ok'})
            try:
                transaction = Transaction.objects.get(provider_transaction_id=airtel_money_id)
            except Transaction.DoesNotExist:
                logger.warning('Airtel transaction not found: ' + str(airtel_money_id))
                return Response({'status': 'ok'})
            if result.get('success'):
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_COMPLETED)
            else:
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_FAILED, reason=result.get('error', 'Airtel payment failed'))
            return Response({'status': 'ok'})
        except Exception as e:
            logger.error('Airtel callback error: ' + str(e))
            return Response({'status': 'ok'})


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            provider = StripeProvider()
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
            result = provider.handle_callback(request.data, sig_header=sig_header)
            if result.get('success') is None:
                return Response({'status': 'ok'})
            internal_ref = result.get('internal_ref', '')
            if not internal_ref:
                return Response({'status': 'ok'})
            try:
                transaction = Transaction.objects.get(internal_ref=internal_ref)
            except Transaction.DoesNotExist:
                logger.warning('Stripe transaction not found: ' + internal_ref)
                return Response({'status': 'ok'})
            if result.get('success'):
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_COMPLETED)
            else:
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_FAILED, reason=result.get('error', 'Stripe payment failed'))
            return Response({'status': 'ok'})
        except Exception as e:
            logger.error('Stripe webhook error: ' + str(e))
            return Response({'status': 'ok'})


class FlutterwaveWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            provider = FlutterwaveProvider()
            result = provider.handle_callback(request.data)
            if result.get('success') is None:
                return Response({'status': 'ok'})
            tx_ref = result.get('tx_ref', '')
            if not tx_ref:
                return Response({'status': 'ok'})
            try:
                transaction = Transaction.objects.get(internal_ref=tx_ref)
            except Transaction.DoesNotExist:
                logger.warning('Flutterwave transaction not found: ' + tx_ref)
                return Response({'status': 'ok'})
            if result.get('success'):
                transaction.provider_transaction_id = result.get('transaction_id', '')
                transaction.save(update_fields=['provider_transaction_id'])
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_COMPLETED)
            else:
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_FAILED, reason='Flutterwave payment failed')
            return Response({'status': 'ok'})
        except Exception as e:
            logger.error('Flutterwave webhook error: ' + str(e))
            return Response({'status': 'ok'})


class PayPalWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            provider = PayPalProvider()
            result = provider.handle_callback(request.data)
            if result.get('success') is None:
                return Response({'status': 'ok'})
            order_id = result.get('order_id', '')
            if not order_id:
                return Response({'status': 'ok'})
            try:
                transaction = Transaction.objects.get(provider_transaction_id=order_id)
            except Transaction.DoesNotExist:
                logger.warning('PayPal transaction not found: ' + order_id)
                return Response({'status': 'ok'})
            if result.get('success'):
                transaction.provider_meta.update({'capture_id': result.get('capture_id', '')})
                transaction.save(update_fields=['provider_meta'])
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_COMPLETED)
            else:
                if transaction.status == Transaction.STATUS_PROCESSING:
                    transaction.transition_to(Transaction.STATUS_FAILED, reason='PayPal payment failed')
            return Response({'status': 'ok'})
        except Exception as e:
            logger.error('PayPal webhook error: ' + str(e))
            return Response({'status': 'ok'})
