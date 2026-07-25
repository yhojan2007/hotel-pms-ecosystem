from app.services.payment_gateways.base import BasePaymentGateway
from app.services.payment_gateways.mock_gateway import MockPaymentGateway
from app.services.payment_gateways.wallbit_gateway import WallbitPaymentGateway
from app.services.payment_gateways.mercadopago_gateway import MercadoPagoPaymentGateway
from app.services.payment_gateways.stripe_gateway import StripePaymentGateway

class PaymentGatewayFactory:
    """Factory para instanciar la pasarela de pago configurada sin alterar el código de negocio."""

    @staticmethod
    def get_gateway(provider_name: str = "mock") -> BasePaymentGateway:
        provider = provider_name.lower().strip()
        
        if provider == "wallbit":
            return WallbitPaymentGateway()
        elif provider == "mercadopago":
            return MercadoPagoPaymentGateway()
        elif provider == "stripe":
            return StripePaymentGateway()
        else:
            return MockPaymentGateway()
