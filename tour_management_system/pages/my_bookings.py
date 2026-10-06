from datetime import date, timedelta

import streamlit as st

from auth import current_user, require_role
from config import ROLES
from services.booking_service import cancel_booking, get_booking, get_user_bookings, modify_booking
from utils.helpers import money, receipt_text, status_badge


def status_flow(status: str, payment_status: str):
    if status == "Cancelled":
        steps = [("Booked", True, ""), ("Cancelled", True, "cancelled")]
    else:
        steps = [
            ("Booked", True, ""),
            ("Payment Confirmed", payment_status == "Paid", ""),
            ("Tour Confirmed", status in ["Confirmed", "Modified", "Completed"], ""),
            ("Completed", status == "Completed", ""),
        ]
    html = "<div class='status-flow'>"
    for label, active, extra in steps:
        klass = "status-step"
        if active:
            klass += " active"
        if extra:
            klass += f" {extra}"
        html += f"<span class='{klass}'>{label}</span>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render():
    if not require_role(ROLES["CUSTOMER"]):
        return
    user = current_user()
    bookings = get_user_bookings(user["id"])
    st.title("My Bookings")
    if not bookings:
        st.info("You do not have any bookings yet.")
        return

    for booking in bookings:
        with st.container():
            st.markdown(
                f"""
                <div class='tm-card'>
                    <h3>#{booking.id} - {booking.tour.title}</h3>
                    <div class='muted'>{booking.tour.destination} | Travel date: {booking.travel_date.strftime('%d %b %Y')}</div>
                    <p>{booking.travelers} traveler(s) | {money(booking.total_amount)}</p>
                    <p>{status_badge(booking.status)} {status_badge(booking.payment_status)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            status_flow(booking.status, booking.payment_status)
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("View Details", key=f"view_{booking.id}", use_container_width=True):
                st.session_state.expanded_booking_id = booking.id
            if c2.button("Modify", key=f"modify_{booking.id}", use_container_width=True, disabled=booking.status in ["Cancelled", "Completed"]):
                st.session_state.modify_booking_id = booking.id
            if c3.button("Cancel", key=f"cancel_{booking.id}", use_container_width=True, disabled=booking.status in ["Cancelled", "Completed"]):
                st.session_state.cancel_booking_id = booking.id
            if c4.button("Pay", key=f"pay_{booking.id}", use_container_width=True, disabled=booking.payment_status == "Paid" or booking.status == "Cancelled"):
                st.session_state.payment_booking_id = booking.id
                st.session_state.page = "Payment"
                st.rerun()

    selected_id = st.session_state.get("expanded_booking_id")
    if selected_id:
        booking = get_booking(selected_id)
        if booking:
            st.markdown("### Booking Details")
            st.write(f"Special requests: {booking.special_requests or '-'}")
            payment = booking.payments[-1] if booking.payments else None
            st.download_button(
                "Download Receipt",
                data=receipt_text(booking, payment).encode("utf-8"),
                file_name=f"booking_receipt_{booking.id}.txt",
                mime="text/plain",
            )

    modify_id = st.session_state.get("modify_booking_id")
    if modify_id:
        booking = get_booking(modify_id)
        if booking:
            st.markdown("### Modify Booking")
            with st.form("modify_booking_form"):
                new_date = st.date_input("Travel Date", min_value=date.today(), value=max(date.today() + timedelta(days=1), booking.travel_date))
                new_travelers = st.number_input("Travelers", min_value=1, value=booking.travelers)
                special = st.text_area("Special Requests", value=booking.special_requests or "")
                submitted = st.form_submit_button("Save Changes", type="primary")
            if submitted:
                ok, message = modify_booking(booking.id, new_date, new_travelers, special)
                if ok:
                    st.success(message)
                    st.session_state.pop("modify_booking_id", None)
                    st.rerun()
                else:
                    st.error(message)

    cancel_id = st.session_state.get("cancel_booking_id")
    if cancel_id:
        booking = get_booking(cancel_id)
        if booking:
            st.warning(f"Confirm cancellation for booking #{booking.id} ({booking.tour.title}).")
            c1, c2 = st.columns(2)
            if c1.button("Confirm Cancellation", type="primary", use_container_width=True):
                ok, message = cancel_booking(booking.id)
                if ok:
                    st.success(message)
                    st.session_state.pop("cancel_booking_id", None)
                    st.rerun()
                else:
                    st.error(message)
            if c2.button("Keep Booking", use_container_width=True):
                st.session_state.pop("cancel_booking_id", None)
                st.rerun()
