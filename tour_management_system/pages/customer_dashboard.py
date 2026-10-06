from datetime import date

import streamlit as st

from auth import current_user, require_role
from config import ROLES
from services.booking_service import get_active_tours, get_user_bookings, search_tours
from utils.helpers import metric_card, tour_card


def render():
    if not require_role(ROLES["CUSTOMER"]):
        return
    user = current_user()
    bookings = get_user_bookings(user["id"])
    active_bookings = [b for b in bookings if b.status in ["Pending Payment", "Confirmed", "Modified"]]
    upcoming = sorted([b for b in active_bookings if b.travel_date >= date.today()], key=lambda b: b.travel_date)

    st.title(f"Welcome, {user['name'].split()[0]}")
    st.caption("Find curated tours, manage bookings, and track payment status from one clean dashboard.")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total Bookings", len(bookings))
    with c2:
        metric_card("Active Bookings", len(active_bookings))
    with c3:
        metric_card("Upcoming Tour", upcoming[0].tour.destination if upcoming else "None")

    st.markdown("### Search Tours")
    with st.form("dashboard_search"):
        q = st.text_input("Destination", placeholder="Try Goa, Bali, Jaipur...")
        submitted = st.form_submit_button("Search", type="primary")
    if submitted:
        st.session_state.dashboard_search = q
        st.session_state.page = "Search Tours"
        st.rerun()

    st.markdown("### Upcoming Booking")
    if upcoming:
        b = upcoming[0]
        st.markdown(
            f"""
            <div class='tm-card'>
                <h3>{b.tour.title}</h3>
                <div class='muted'>{b.tour.destination} | Travel date: {b.travel_date.strftime('%d %b %Y')}</div>
                <p>{b.travelers} traveler(s), status: <strong>{b.status}</strong>, payment: <strong>{b.payment_status}</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No upcoming booking yet. Choose a package and start planning.")

    st.markdown("### Featured Packages")
    tours = search_tours(available_only=True)[:6]
    cols = st.columns(3)
    for index, tour in enumerate(tours):
        with cols[index % 3]:
            tour_card(tour, "dash")

    st.markdown("### Popular Destinations")
    destinations = sorted({tour.destination for tour in get_active_tours()})[:8]
    st.write(" | ".join(destinations))
