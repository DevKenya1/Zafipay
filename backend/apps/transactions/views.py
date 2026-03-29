import uuid
import logging
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Transaction
from .serializers import InitiatePaymentSerializer, TransactionSerializer
from apps.providers.router import get_provider

logger = logging.getLogger(__name__)

METHOD_MAP = {
    'mpesa': 'stk_push',
    'airtel': 'airtel_money',
    'stripe': 'card',
    'flutterwave': 'card',
    'paypal': 'paypal',
}


class InitiatePaymentView(APIView):

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        internal_ref = str(uuid.uuid4()).replace('-', '')[:20]

        transaction = Transaction.objects.create(
            merchant=request.user.merchant,
            reference=data['reference'],
            internal_ref=internal_ref,
            provider=data['provider'],
            method=METHOD_MAP.get(data['provider'], 'card'),
            amount=data['amount'],
            currency=data.get('currency', 'KES'),
            phone=data.get('phone', ''),
            status=Transaction.STATUS_PENDING,
        )

        try:
            provider = get_provider(data['provider'])
            result = provider.initiate_payment(transaction)

            if result.get('success'):
                checkout_request_id = result.get('checkout_request_id', '')
                transaction.provider_transaction_id = checkout_request_id
                transaction.provider_meta = result.get('raw', {})
                transaction.save(update_fields=['provider_transaction_id', 'provider_meta', 'updated_at'])
                transaction.transition_to(Transaction.STATUS_PROCESSING)
                return Response({
                    'success': True,
                    'message': 'Payment initiated. Please complete on your phone.',
                    'transaction_id': str(transaction.id),
                    'internal_ref': transaction.internal_ref,
                    'checkout_request_id': checkout_request_id,
                }, status=status.HTTP_201_CREATED)
            else:
                transaction.transition_to(
                    Transaction.STATUS_FAILED,
                    reason=result.get('error', 'Provider error')
                )
                return Response({
                    'success': False,
                    'message': result.get('error', 'Payment initiation failed.'),
                    'transaction_id': str(transaction.id),
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error('Payment initiation error: ' + str(e))
            transaction.transition_to(Transaction.STATUS_FAILED, reason=str(e))
            return Response({
                'success': False,
                'message': 'An error occurred initiating payment.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            merchant=self.request.user.merchant
        ).prefetch_related('events')


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            merchant=self.request.user.merchant
        ).prefetch_related('events')
