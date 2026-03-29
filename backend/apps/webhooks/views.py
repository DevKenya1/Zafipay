import secrets
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WebhookEndpoint, WebhookDelivery
from .serializers import (
    WebhookEndpointSerializer,
    CreateWebhookEndpointSerializer,
    WebhookDeliverySerializer,
)


class WebhookEndpointListCreateView(APIView):

    def get(self, request):
        endpoints = WebhookEndpoint.objects.filter(merchant=request.user.merchant)
        return Response(WebhookEndpointSerializer(endpoints, many=True).data)

    def post(self, request):
        serializer = CreateWebhookEndpointSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        secret = 'whsec_' + secrets.token_urlsafe(32)
        endpoint = WebhookEndpoint.objects.create(
            merchant=request.user.merchant,
            url=serializer.validated_data['url'],
            events=serializer.validated_data['events'],
            secret=secret,
        )
        data = WebhookEndpointSerializer(endpoint).data
        data['secret'] = secret
        data['warning'] = 'Save this secret now. It will never be shown again.'
        return Response(data, status=status.HTTP_201_CREATED)


class WebhookEndpointDetailView(APIView):

    def get_object(self, pk, merchant):
        try:
            return WebhookEndpoint.objects.get(pk=pk, merchant=merchant)
        except WebhookEndpoint.DoesNotExist:
            return None

    def delete(self, request, pk):
        endpoint = self.get_object(pk, request.user.merchant)
        if not endpoint:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        endpoint.is_active = False
        endpoint.save(update_fields=['is_active'])
        return Response({'message': 'Webhook endpoint disabled.'})

    def patch(self, request, pk):
        endpoint = self.get_object(pk, request.user.merchant)
        if not endpoint:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CreateWebhookEndpointSerializer(endpoint, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(WebhookEndpointSerializer(endpoint).data)


class WebhookDeliveryListView(generics.ListAPIView):
    serializer_class = WebhookDeliverySerializer

    def get_queryset(self):
        return WebhookDelivery.objects.filter(
            endpoint__merchant=self.request.user.merchant
        ).select_related('endpoint', 'transaction')


class WebhookDeliveryRetryView(APIView):

    def post(self, request, pk):
        try:
            delivery = WebhookDelivery.objects.get(
                pk=pk,
                endpoint__merchant=request.user.merchant,
            )
            if delivery.status == WebhookDelivery.STATUS_SUCCESS:
                return Response({'error': 'Delivery already succeeded.'}, status=status.HTTP_400_BAD_REQUEST)
            from .tasks import deliver_webhook
            deliver_webhook.delay(str(delivery.id))
            return Response({'message': 'Retry queued.'})
        except WebhookDelivery.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
