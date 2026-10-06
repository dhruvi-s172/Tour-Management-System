import streamlit as st

from auth import require_role
from config import ROLES
from services.booking_service import get_tour
from utils.helpers import money


def render():
    if not require_role(ROLES["CUSTOMER"]):
        return
    tour_id = st.session_state.get("selected_tour_id")
    if not tour_id:
        st.warning("Select a tour package first.")
        if st.button("Go to Search"):
            st.session_state.page = "Search Tours"
            st.rerun()
        return
    tour = get_tour(tour_id)
    if not tour:
        st.error("Selected tour package was not found.")
        return

    st.markdown(f"<img class='detail-img' src='{tour.image_url}' onerror=\"this.style.display='none'\">", unsafe_allow_html=True)
    st.title(tour.title)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Destination", tour.destination)
    c2.metric("Duration", f"{tour.duration_days} days")
    c3.metric("Price", money(tour.price))
    c4.metric("Seats", f"{tour.available_seats}/{tour.total_seats}")

    st.markdown("### Overview")
    st.write(tour.description)
    st.markdown("### Day-wise Itinerary")
    for line in tour.itinerary.splitlines():
        st.markdown(f"- {line}")
    st.markdown("### Included Facilities")
    st.write("Hotel stay, guided sightseeing, selected meals, local transport, booking support, and a simulated digital payment receipt.")
    st.markdown("### Booking Information")
    st.info("Bookings reserve seats immediately and remain Pending Payment until the demo payment gateway confirms payment.")

    if st.button("Book Now", type="primary", use_container_width=True, disabled=tour.available_seats <= 0):
        st.session_state.page = "Booking"
        st.rerun()
