from rest_framework import serializers
from .models import Refund
from apps.transactions.models import Transaction


class InitiateRefundSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate(self, data):
        try:
            transaction = Transaction.objects.get(
                id=data['transaction_id'],
                merchant=self.context['request'].user.merchant,
            )
        except Transaction.DoesNotExist:
            raise serializers.ValidationError('Transaction not found.')

        if transaction.status != Transaction.STATUS_COMPLETED:
            raise serializers.ValidationError('Only completed transactions can be refunded.')

        if data['amount'] > transaction.amount:
            raise serializers.ValidationError('Refund amount cannot exceed transaction amount.')

        if data['amount'] <= 0:
            raise serializers.ValidationError('Refund amount must be greater than 0.')

        data['transaction'] = transaction
        return data


class RefundSerializer(serializers.ModelSerializer):
    transaction_ref = serializers.CharField(source='transaction.internal_ref', read_only=True)
    provider = serializers.CharField(source='transaction.provider', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'transaction_ref', 'provider', 'amount',
            'reason', 'status', 'provider_refund_id',
            'failure_reason', 'created_at', 'updated_at',
        ]
        read_only_fields = fields
