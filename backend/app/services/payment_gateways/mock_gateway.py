from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.payment_gateways.base import BasePaymentGateway

class MockPaymentGateway(BasePaymentGateway):
    """Pasarela de pago de prueba para entornos de desarrollo y demostración en vivo."""

    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        payment_url = f"{settings.BACKEND_PUBLIC_URL.rstrip('/')}{settings.API_V1_STR}/webhooks/payments/mock?booking_id={booking_id}&monto={monto}"
        return {
            "provider": "mock",
            "payment_url": payment_url,
            "booking_id": booking_id,
            "monto": monto,
            "status": "created"
        }

    def parse_webhook_payload(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        booking_id = int(payload.get("booking_id", 0))
        monto = float(payload.get("monto", 0.0))
        transaction_ref = payload.get("transaction_ref") or payload.get("referencia") or f"tx_mock_{booking_id}"
        
        return {
            "booking_id": booking_id,
            "monto": monto,
            "is_success": True,
            "referencia": transaction_ref,
            "provider": "mock"
        }
