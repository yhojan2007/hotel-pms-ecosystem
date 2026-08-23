"""Factory que elige la implementación de pasarela por nombre."""

from app.services.payment_gateways.base import BasePaymentGateway
from app.services.payment_gateways.mercadopago_gateway import MercadoPagoPaymentGateway
from app.services.payment_gateways.mock_gateway import MockPaymentGateway
from app.services.payment_gateways.stripe_gateway import StripePaymentGateway
from app.services.payment_gateways.wallbit_gateway import WallbitPaymentGateway


class PaymentGatewayFactory:
    """Instancia Wallbit, MercadoPago, Stripe o mock según ``provider_name``."""

    @staticmethod
    def get_gateway(provider_name: str = "mock") -> BasePaymentGateway:
        """Devuelve la pasarela pedida; cualquier valor desconocido cae a mock."""
        provider = provider_name.lower().strip()

        if provider == "wallbit":
            return WallbitPaymentGateway()
        elif provider == "mercadopago":
            return MercadoPagoPaymentGateway()
        elif provider == "stripe":
            return StripePaymentGateway()
        else:
            return MockPaymentGateway()
