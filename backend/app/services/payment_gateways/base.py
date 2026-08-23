"""Contrato común de pasarelas de pago."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BasePaymentGateway(ABC):
    """Interfaz para generar links de cobro y normalizar webhooks."""

    @abstractmethod
    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        """Genera una URL de pago para la reserva especificada."""
        pass

    @abstractmethod
    def parse_webhook_payload(
        self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Normaliza el webhook del proveedor.

        Retorna:
            ``{"booking_id": int, "monto": float, "is_success": bool, "referencia": str}``
        """
        pass
