from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePaymentGateway(ABC):
    """
    Clase base abstracta para pasarelas de pago modulares.
    Permite intercambiar entre Wallbit, MercadoPago, Stripe o Mock fácilmente.
    """

    @abstractmethod
    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        """Genera una URL de pago para la reserva especificada."""
        pass

    @abstractmethod
    def parse_webhook_payload(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Analiza el payload recibido por webhook del proveedor de pago.
        Retorna una estructura estandarizada:
        { "booking_id": int, "monto": float, "is_success": bool, "referencia": str }
        """
        pass
