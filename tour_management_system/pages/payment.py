import streamlit as st

from auth import require_role
from config import ROLES
from services.booking_service import get_booking
from services.payment_service import PAYMENT_METHODS, latest_payment_for_booking, process_payment, validate_payment
from utils.helpers import money, receipt_text, status_badge


def render_confirmation(booking):
    payment = latest_payment_for_booking(booking.id)
    st.success("Booking confirmed successfully.")
    st.markdown("### Booking Confirmation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Booking ID", booking.id)
    c2.metric("Travelers", booking.travelers)
    c3.metric("Total Amount", money(booking.total_amount))
    st.markdown(
        f"""
        <div class='tm-card'>
            <h3>{booking.tour.title}</h3>
            <p><strong>Customer:</strong> {booking.user.name}</p>
            <p><strong>Destination:</strong> {booking.tour.destination}</p>
            <p><strong>Travel Date:</strong> {booking.travel_date.strftime('%d %b %Y')}</p>
            <p><strong>Booking Status:</strong> {status_badge(booking.status)}</p>
            <p><strong>Payment Status:</strong> {status_badge(booking.payment_status)}</p>
            <p><strong>Transaction ID:</strong> {payment.transaction_id if payment else '-'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download Receipt",
        data=receipt_text(booking, payment).encode("utf-8"),
        file_name=f"booking_receipt_{booking.id}.txt",
        mime="text/plain",
        use_container_width=True,
    )


def render():
    if not require_role(ROLES["CUSTOMER"]):
        return
    booking_id = st.session_state.get("payment_booking_id") or st.session_state.get("selected_booking_id")
    if not booking_id:
        st.warning("No booking selected for payment.")
        return
    booking = get_booking(booking_id)
    if not booking:
        st.error("Booking was not found.")
        return

    st.title("Demo Payment Gateway")
    st.info("This is a simulated offline payment gateway for academic demonstration. No real money is processed.")
    if booking.payment_status == "Paid":
        render_confirmation(booking)
        return

    st.markdown(
        f"""
        <div class='tm-card'>
            <h3>Pay for Booking #{booking.id}</h3>
            <div>{booking.tour.title} - {booking.tour.destination}</div>
            <div class='price'>{money(booking.total_amount)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("payment_form"):
        method = st.selectbox("Payment Method", PAYMENT_METHODS)
        payer_name = st.text_input("Payer Name", value=booking.user.name)
        label = "UPI ID" if method == "UPI" else "Card / Banking Reference"
        reference_value = st.text_input(label, placeholder="student@upi or demo card number")
        force_status = st.radio("Demo Result", ["Success", "Failed", "Auto"], horizontal=True)
        submitted = st.form_submit_button("Pay Securely", type="primary", use_container_width=True)

    if submitted:
        valid, message = validate_payment(method, payer_name, reference_value)
        if not valid:
            st.error(message)
            return
        ok, message, result = process_payment(booking.id, booking.total_amount, method, force_status)
        if ok:
            st.success(message)
            st.session_state.selected_booking_id = booking.id
            st.rerun()
        else:
            st.error(message)
            if result:
                st.caption(f"Transaction ID: {result['transaction_id']}")
