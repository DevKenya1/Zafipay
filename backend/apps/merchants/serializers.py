from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Merchant, APIKey


class RegisterSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True, default='KE')
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'business_name', 'phone', 'country']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        phone = validated_data.pop('phone')
        country = validated_data.pop('country', 'KE')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        Merchant.objects.create(
            user=user,
            business_name=business_name,
            email=validated_data['email'],
            phone=phone,
            country=country,
        )
        return user


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'business_name', 'email', 'phone', 'country', 'mode', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'prefix', 'scope', 'is_active', 'last_used_at', 'expires_at', 'created_at']
        read_only_fields = ['id', 'prefix', 'last_used_at', 'created_at']


class CreateAPIKeySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    scope = serializers.ChoiceField(choices=APIKey.SCOPE_CHOICES, default=APIKey.SCOPE_FULL)