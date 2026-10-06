import pandas as pd
import streamlit as st

from auth import require_role
from config import BOOKING_STATUSES, ROLES
from services.booking_service import get_all_bookings, update_booking_status
from utils.helpers import money, status_badge


def render():
    if not require_role(ROLES["ADMIN"]):
        return
    st.title("Manage Bookings")
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search bookings", placeholder="Booking ID, customer, tour, destination")
    status = c2.selectbox("Status", ["All"] + BOOKING_STATUSES)
    bookings = get_all_bookings(status, search)

    if bookings:
        table = pd.DataFrame(
            [
                {
                    "ID": b.id,
                    "Customer": b.user.name,
                    "Email": b.user.email,
                    "Tour": b.tour.title,
                    "Destination": b.tour.destination,
                    "Travel Date": b.travel_date,
                    "Travelers": b.travelers,
                    "Amount": b.total_amount,
                    "Status": b.status,
                    "Payment": b.payment_status,
                }
                for b in bookings
            ]
        )
        st.dataframe(table, use_container_width=True, hide_index=True)
    else:
        st.info("No bookings match your filters.")

    st.markdown("### Update Booking")
    if bookings:
        selected = st.selectbox("Select Booking", bookings, format_func=lambda b: f"#{b.id} - {b.user.name} - {b.tour.title}")
        st.markdown(
            f"""
            <div class='tm-card'>
                <p><strong>Customer:</strong> {selected.user.name} ({selected.user.email})</p>
                <p><strong>Tour:</strong> {selected.tour.title}, {selected.tour.destination}</p>
                <p><strong>Amount:</strong> {money(selected.total_amount)}</p>
                <p>{status_badge(selected.status)} {status_badge(selected.payment_status)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        new_status = st.selectbox("New Booking Status", BOOKING_STATUSES, index=BOOKING_STATUSES.index(selected.status) if selected.status in BOOKING_STATUSES else 0)
        if st.button("Update Status", type="primary", use_container_width=True):
            ok, message = update_booking_status(selected.id, new_status)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
