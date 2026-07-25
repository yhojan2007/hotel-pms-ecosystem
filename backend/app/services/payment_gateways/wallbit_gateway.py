from typing import Dict, Any, Optional
from app.services.payment_gateways.base import BasePaymentGateway

class WallbitPaymentGateway(BasePaymentGateway):
    """Pasarela de pago modular para integración con la API de Wallbit."""

    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        # En producción se realiza una llamada HTTP POST a la API de Wallbit
        payment_url = f"https://wallbit.io/checkout/pay?booking_id={booking_id}&amount={monto}"
        return {
            "provider": "wallbit",
            "payment_url": payment_url,
            "booking_id": booking_id,
            "monto": monto,
            "status": "pending_wallbit"
        }

    def parse_webhook_payload(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        data = payload.get("data", payload)
        booking_id = int(data.get("booking_id") or data.get("external_reference", 0))
        monto = float(data.get("amount") or data.get("monto", 0.0))
        event_status = data.get("status", "completed")
        
        return {
            "booking_id": booking_id,
            "monto": monto,
            "is_success": event_status in ["completed", "approved", "success"],
            "referencia": data.get("id", f"wb_tx_{booking_id}"),
            "provider": "wallbit"
        }
