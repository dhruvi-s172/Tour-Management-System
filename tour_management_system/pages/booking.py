from datetime import date, timedelta

import streamlit as st

from auth import current_user, require_role
from config import ROLES
from services.booking_service import create_booking, get_tour
from utils.helpers import money


def render():
    if not require_role(ROLES["CUSTOMER"]):
        return
    tour_id = st.session_state.get("selected_tour_id")
    if not tour_id:
        st.warning("Choose a package before booking.")
        if st.button("Search Tours"):
            st.session_state.page = "Search Tours"
            st.rerun()
        return
    tour = get_tour(tour_id)
    if not tour:
        st.error("Tour package was not found.")
        return

    st.title("Create Booking")
    st.markdown(
        f"""
        <div class='tm-card'>
            <h3>{tour.title}</h3>
            <div class='muted'>{tour.destination} | {tour.duration_days} days | {tour.category}</div>
            <div class='price'>{money(tour.price)} per person</div>
            <div class='tiny muted'>{tour.available_seats} seats available</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("booking_form"):
        travel_date = st.date_input("Travel Date", min_value=date.today(), value=date.today() + timedelta(days=14))
        travelers = st.number_input("Number of Travelers", min_value=1, max_value=max(1, tour.available_seats), value=1)
        special_requests = st.text_area("Special Requests", placeholder="Meal preference, pickup notes, room preferences...")
        st.metric("Total Price", money(tour.price * travelers))
        submitted = st.form_submit_button("Confirm Booking", type="primary", use_container_width=True)

    if submitted:
        ok, message, booking_id = create_booking(current_user()["id"], tour.id, travel_date, travelers, special_requests)
        if ok:
            st.success(message)
            st.session_state.payment_booking_id = booking_id
            st.session_state.page = "Payment"
            st.rerun()
        else:
            st.error(message)
