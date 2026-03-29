from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Merchant, APIKey
from .serializers import (
    RegisterSerializer, MerchantSerializer,
    APIKeySerializer, CreateAPIKeySerializer
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Merchant registered successfully.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class MerchantProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = MerchantSerializer

    def get_object(self):
        return self.request.user.merchant


class ToggleModeView(APIView):
    def post(self, request):
        merchant = request.user.merchant
        merchant.mode = 'live' if merchant.mode == 'test' else 'test'
        merchant.save(update_fields=['mode'])
        return Response({
            'mode': merchant.mode,
            'message': f'Switched to {merchant.mode} mode.'
        })


class APIKeyListCreateView(APIView):
    def get(self, request):
        keys = APIKey.objects.filter(merchant=request.user.merchant)
        return Response(APIKeySerializer(keys, many=True).data)

    def post(self, request):
        serializer = CreateAPIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key, raw_key = APIKey.generate(
            merchant=request.user.merchant,
            name=serializer.validated_data['name'],
            scope=serializer.validated_data['scope'],
        )
        data = APIKeySerializer(api_key).data
        data['key'] = raw_key
        data['warning'] = 'Save this key now. It will never be shown again.'
        return Response(data, status=status.HTTP_201_CREATED)


class APIKeyRevokeView(APIView):
    def post(self, request, pk):
        try:
            key = APIKey.objects.get(pk=pk, merchant=request.user.merchant)
            key.is_active = False
            key.save(update_fields=['is_active'])
            return Response({'message': 'API key revoked.'})
        except APIKey.DoesNotExist:
            return Response({'error': 'Key not found.'}, status=status.HTTP_404_NOT_FOUND)