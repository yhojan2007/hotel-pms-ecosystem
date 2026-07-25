from typing import Dict, Any, Optional
from app.services.payment_gateways.base import BasePaymentGateway

class StripePaymentGateway(BasePaymentGateway):
    """Pasarela de pago modular para integración con Stripe Checkout."""

    def create_payment_link(self, booking_id: int, monto: float, descripcion: str) -> Dict[str, Any]:
        payment_url = f"https://checkout.stripe.com/pay/cs_test_{booking_id}"
        return {
            "provider": "stripe",
            "payment_url": payment_url,
            "booking_id": booking_id,
            "monto": monto,
            "status": "pending_stripe"
        }

    def parse_webhook_payload(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        event_type = payload.get("type", "checkout.session.completed")
        data_obj = payload.get("data", {}).get("object", payload)
        
        booking_id = int(data_obj.get("metadata", {}).get("booking_id") or data_obj.get("booking_id", 0))
        monto = float(data_obj.get("amount_total", 0) / 100 if "amount_total" in data_obj else data_obj.get("monto", 0.0))
        
        return {
            "booking_id": booking_id,
            "monto": monto,
            "is_success": event_type in ["checkout.session.completed", "payment_intent.succeeded"],
            "referencia": data_obj.get("id", f"ch_stripe_{booking_id}"),
            "provider": "stripe"
        }
