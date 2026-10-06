import streamlit as st

from auth import require_role
from config import ROLES, TOUR_CATEGORIES
from services.booking_service import search_tours
from utils.helpers import tour_card


def render():
    if not require_role(ROLES["CUSTOMER"]):
        return
    st.title("Search Tour Packages")
    default_destination = st.session_state.pop("dashboard_search", "")

    with st.form("tour_search_form"):
        c1, c2, c3 = st.columns([1.3, 1, 1])
        destination = c1.text_input("Destination", value=default_destination)
        category = c2.selectbox("Category", ["All"] + TOUR_CATEGORIES)
        available_only = c3.checkbox("Available only", value=True)
        c4, c5, c6 = st.columns(3)
        min_budget = c4.number_input("Minimum Budget", min_value=0, value=0, step=1000)
        max_budget = c5.number_input("Maximum Budget", min_value=0, value=200000, step=1000)
        max_duration = c6.slider("Maximum Duration", min_value=1, max_value=15, value=10)
        submitted = st.form_submit_button("Apply Filters", type="primary", use_container_width=True)

    tours = search_tours(destination, category, min_budget, max_budget, max_duration, available_only)
    st.caption(f"{len(tours)} package(s) found")
    if not tours:
        st.warning("No packages match the selected filters.")
        return

    cols = st.columns(3)
    for index, tour in enumerate(tours):
        with cols[index % 3]:
            tour_card(tour, "search")
