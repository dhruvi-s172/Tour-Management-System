import random
import uuid
from datetime import datetime

from database import get_session
from models import Booking, Payment


PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking"]


def validate_payment(method: str, payer_name: str, reference_value: str):
    if method not in PAYMENT_METHODS:
        return False, "Select a valid payment method."
    if not payer_name.strip():
        return False, "Payer name is required."
    if not reference_value.strip():
        return False, "Payment reference details are required."
    if method == "UPI" and "@" not in reference_value:
        return False, "Enter a valid demo UPI ID, for example student@upi."
    if method in ["Credit Card", "Debit Card"] and len(reference_value.replace(" ", "")) < 12:
        return False, "Enter at least 12 digits for the demo card number."
    return True, ""


def process_payment(booking_id: int, amount: float, method: str, force_status: str = "Auto"):
    with get_session() as session:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False, "Booking was not found.", None
        if booking.status == "Cancelled":
            return False, "Cancelled bookings cannot be paid.", None
        if abs(float(amount) - float(booking.total_amount)) > 0.01:
            return False, "Payment amount does not match the booking total.", None

        if force_status == "Success":
            status = "SUCCESS"
        elif force_status == "Failed":
            status = "FAILED"
        else:
            status = "SUCCESS" if random.random() > 0.12 else "FAILED"

        transaction_id = f"TXN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        payment = Payment(
            booking_id=booking_id,
            transaction_id=transaction_id,
            amount=amount,
            payment_method=method,
            status=status,
        )
        session.add(payment)

        if status == "SUCCESS":
            booking.payment_status = "Paid"
            booking.status = "Confirmed"
            message = "Payment successful. Booking confirmed."
            ok = True
        else:
            booking.payment_status = "Failed"
            booking.status = "Pending Payment"
            message = "Payment failed. Please try again."
            ok = False
        session.flush()
        payment_id = payment.id
    return ok, message, {"payment_id": payment_id, "transaction_id": transaction_id, "status": status}


def latest_payment_for_booking(booking_id: int):
    with get_session() as session:
        return (
            session.query(Payment)
            .filter(Payment.booking_id == booking_id)
            .order_by(Payment.payment_date.desc())
            .first()
        )
