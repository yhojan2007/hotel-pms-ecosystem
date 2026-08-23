"""Adaptador de payload/URL para Mercado Pago (demo, sin HTTP real)."""

from typing import Any, Dict, Optional

from app.services.payment_gateways.base import BasePaymentGateway


class MercadoPagoPaymentGateway(BasePaymentGateway):
    """Estructura de preferencias y notificaciones al estilo Mercado Pago."""

    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        """Devuelve una URL de redirect de ejemplo."""
        payment_url = f"https://www.mercadopago.com/checkout/v1/redirect?pref_id=demo_{booking_id}"
        return {
            "provider": "mercadopago",
            "payment_url": payment_url,
            "booking_id": booking_id,
            "monto": monto,
            "status": "pending_mp",
        }

    def parse_webhook_payload(
        self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Lee ``external_reference`` y ``transaction_amount``."""
        data = payload.get("data", payload)
        booking_id = int(data.get("external_reference") or payload.get("booking_id", 0))
        monto = float(data.get("transaction_amount") or payload.get("monto", 0.0))
        status = data.get("status") or payload.get("status", "approved")

        return {
            "booking_id": booking_id,
            "monto": monto,
            "is_success": status in ["approved", "accredited"],
            "referencia": str(data.get("id") or f"mp_ref_{booking_id}"),
            "provider": "mercadopago",
        }
