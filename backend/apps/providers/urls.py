from django.urls import path
from . import views

urlpatterns = [
    path('mpesa/callback/', views.MpesaCallbackView.as_view(), name='mpesa_callback'),
    path('airtel/callback/', views.AirtelCallbackView.as_view(), name='airtel_callback'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('flutterwave/webhook/', views.FlutterwaveWebhookView.as_view(), name='flutterwave_webhook'),
    path('paypal/webhook/', views.PayPalWebhookView.as_view(), name='paypal_webhook'),
]
