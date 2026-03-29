import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Refund
from .serializers import InitiateRefundSerializer, RefundSerializer
from apps.providers.router import get_provider
from apps.transactions.models import Transaction

logger = logging.getLogger(__name__)


class InitiateRefundView(APIView):

    def post(self, request):
        serializer = InitiateRefundSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        transaction = data['transaction']

        refund = Refund.objects.create(
            transaction=transaction,
            merchant=request.user.merchant,
            amount=data['amount'],
            reason=data.get('reason', ''),
            status=Refund.STATUS_PENDING,
        )

        try:
            provider = get_provider(transaction.provider)
            result = provider.refund(
                transaction=transaction,
                amount=data['amount'],
                reason=data.get('reason', ''),
            )

            if result.get('success'):
                refund.status = Refund.STATUS_COMPLETED
                refund.provider_refund_id = result.get('refund_id', '')
                refund.provider_meta = result.get('raw', {})
                refund.save()
                transaction.transition_to(Transaction.STATUS_REFUNDED)
                return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
            else:
                refund.status = Refund.STATUS_FAILED
                refund.failure_reason = result.get('error', 'Provider refund failed')
                refund.save()
                return Response({
                    'error': result.get('error', 'Refund failed.'),
                    'refund_id': str(refund.id),
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error('Refund error: ' + str(e))
            refund.status = Refund.STATUS_FAILED
            refund.failure_reason = str(e)
            refund.save()
            return Response({
                'error': 'An error occurred processing the refund.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefundListView(generics.ListAPIView):
    serializer_class = RefundSerializer

    def get_queryset(self):
        return Refund.objects.filter(
            merchant=self.request.user.merchant
        ).select_related('transaction')


class RefundDetailView(generics.RetrieveAPIView):
    serializer_class = RefundSerializer

    def get_queryset(self):
        return Refund.objects.filter(
            merchant=self.request.user.merchant
        ).select_related('transaction')
