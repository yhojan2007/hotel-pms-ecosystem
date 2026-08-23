"""Pasarela mock: el link apunta al webhook local de confirmación."""

from typing import Any, Dict, Optional

from app.core.config import settings
from app.services.payment_gateways.base import BasePaymentGateway


class MockPaymentGateway(BasePaymentGateway):
    """Cobro de demostración; no llama a un proveedor externo."""

    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        """Arma una URL GET al webhook ``/payments/mock`` del propio backend."""
        payment_url = (
            f"{settings.BACKEND_PUBLIC_URL.rstrip('/')}"
            f"{settings.API_V1_STR}/webhooks/payments/mock?booking_id={booking_id}&monto={monto}"
        )
        return {
            "provider": "mock",
            "payment_url": payment_url,
            "booking_id": booking_id,
            "monto": monto,
            "status": "created",
        }

    def parse_webhook_payload(
        self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Lee ``booking_id`` / ``monto`` y marca el cobro como exitoso."""
        booking_id = int(payload.get("booking_id", 0))
        monto = float(payload.get("monto", 0.0))
        transaction_ref = payload.get("transaction_ref") or payload.get("referencia") or f"tx_mock_{booking_id}"

        return {
            "booking_id": booking_id,
            "monto": monto,
            "is_success": True,
            "referencia": transaction_ref,
            "provider": "mock",
        }
