from .mpesa import MpesaProvider
from .airtel import AirtelProvider
from .stripe_provider import StripeProvider
from .flutterwave import FlutterwaveProvider
from .paypal import PayPalProvider


def get_provider(provider_name):
    providers = {
        'mpesa': MpesaProvider,
        'airtel': AirtelProvider,
        'stripe': StripeProvider,
        'flutterwave': FlutterwaveProvider,
        'paypal': PayPalProvider,
    }
    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError('Unknown provider: ' + provider_name)
    return provider_class()
