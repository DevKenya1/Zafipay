from abc import ABC, abstractmethod


class PaymentProvider(ABC):

    @abstractmethod
    def initiate_payment(self, transaction, **kwargs):
        pass

    @abstractmethod
    def verify_payment(self, provider_transaction_id, **kwargs):
        pass

    @abstractmethod
    def refund(self, transaction, amount, reason='', **kwargs):
        pass

    @abstractmethod
    def handle_callback(self, payload, **kwargs):
        pass
