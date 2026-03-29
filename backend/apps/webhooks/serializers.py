from rest_framework import serializers
from .models import WebhookEndpoint, WebhookDelivery


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'url', 'events', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateWebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['url', 'events']

    def validate_url(self, value):
        if not value.startswith('https://'):
            raise serializers.ValidationError('Webhook URL must use HTTPS.')
        return value

    def validate_events(self, value):
        valid_events = [
            'transaction.completed',
            'transaction.failed',
            'transaction.refunded',
            'transaction.processing',
        ]
        for event in value:
            if event not in valid_events:
                raise serializers.ValidationError(f'Invalid event: {event}. Valid events: {valid_events}')
        return value


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'event_type', 'attempt_number',
            'response_status', 'status', 'next_retry_at',
            'delivered_at', 'created_at',
        ]
        read_only_fields = fields
