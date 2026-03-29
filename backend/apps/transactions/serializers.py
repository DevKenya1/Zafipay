import uuid
from rest_framework import serializers
from .models import Transaction, TransactionEvent


class InitiatePaymentSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=Transaction.PROVIDER_CHOICES)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='KES')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    reference = serializers.CharField(max_length=100)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than 0.')
        return value


class TransactionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionEvent
        fields = ['id', 'event_type', 'from_status', 'to_status', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    events = TransactionEventSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'internal_ref', 'provider', 'method',
            'amount', 'currency', 'status', 'phone', 'card_last4',
            'provider_transaction_id', 'failure_reason',
            'created_at', 'updated_at', 'events',
        ]
        read_only_fields = fields
