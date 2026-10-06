import streamlit as st

from auth import require_role
from config import ROLES, TOUR_CATEGORIES
from database import get_session
from models import TourPackage
from services.booking_service import get_active_tours
from utils.validators import validate_non_negative_int, validate_positive_number


def save_tour(data, tour_id=None):
    errors = []
    if not data["title"].strip():
        errors.append("Title is required.")
    if not data["destination"].strip():
        errors.append("Destination is required.")
    ok, message = validate_positive_number(data["duration_days"], "Duration")
    if not ok:
        errors.append(message)
    ok, message = validate_positive_number(data["price"], "Price")
    if not ok:
        errors.append(message)
    for field in ["available_seats", "total_seats"]:
        ok, message = validate_non_negative_int(data[field], field.replace("_", " ").title())
        if not ok:
            errors.append(message)
    if int(data["available_seats"]) > int(data["total_seats"]):
        errors.append("Available seats cannot exceed total seats.")
    if errors:
        return False, errors

    with get_session() as session:
        tour = session.query(TourPackage).filter(TourPackage.id == tour_id).first() if tour_id else TourPackage()
        if not tour:
            return False, ["Tour package was not found."]
        tour.title = data["title"].strip()
        tour.destination = data["destination"].strip()
        tour.description = data["description"].strip()
        tour.itinerary = data["itinerary"].strip()
        tour.duration_days = int(data["duration_days"])
        tour.price = float(data["price"])
        tour.available_seats = int(data["available_seats"])
        tour.total_seats = int(data["total_seats"])
        tour.category = data["category"]
        tour.image_url = data["image_url"].strip()
        tour.is_active = data["is_active"]
        if not tour_id:
            session.add(tour)
    return True, ["Tour package saved successfully."]


def tour_form(prefix: str, existing=None):
    with st.form(f"{prefix}_tour_form"):
        title = st.text_input("Title", value=getattr(existing, "title", ""))
        destination = st.text_input("Destination", value=getattr(existing, "destination", ""))
        category_default = getattr(existing, "category", TOUR_CATEGORIES[0])
        category = st.selectbox("Category", TOUR_CATEGORIES, index=TOUR_CATEGORIES.index(category_default) if category_default in TOUR_CATEGORIES else 0)
        c1, c2, c3 = st.columns(3)
        duration_days = c1.number_input("Duration Days", min_value=1, value=int(getattr(existing, "duration_days", 3)))
        price = c2.number_input("Price", min_value=1.0, value=float(getattr(existing, "price", 10000.0)), step=500.0)
        total_seats = c3.number_input("Total Seats", min_value=0, value=int(getattr(existing, "total_seats", 20)))
        available_seats = st.number_input("Available Seats", min_value=0, value=int(getattr(existing, "available_seats", 20)))
        image_url = st.text_input("Image URL", value=getattr(existing, "image_url", ""))
        description = st.text_area("Description", value=getattr(existing, "description", ""))
        itinerary = st.text_area("Itinerary", value=getattr(existing, "itinerary", "Day 1: Arrival\nDay 2: Sightseeing\nDay 3: Departure"))
        is_active = st.checkbox("Active", value=bool(getattr(existing, "is_active", True)))
        submitted = st.form_submit_button("Save Package", type="primary", use_container_width=True)
    data = {
        "title": title,
        "destination": destination,
        "category": category,
        "duration_days": duration_days,
        "price": price,
        "total_seats": total_seats,
        "available_seats": available_seats,
        "image_url": image_url,
        "description": description,
        "itinerary": itinerary,
        "is_active": is_active,
    }
    return submitted, data


def render():
    if not require_role(ROLES["ADMIN"]):
        return
    st.title("Manage Tour Packages")
    tab_add, tab_view = st.tabs(["Add Package", "View and Edit Packages"])

    with tab_add:
        submitted, data = tour_form("add")
        if submitted:
            ok, messages = save_tour(data)
            if ok:
                st.success(messages[0])
            else:
                for message in messages:
                    st.error(message)

    with tab_view:
        tours = get_active_tours()
        if not tours:
            st.info("No active tour packages.")
        for tour in tours:
            with st.expander(f"{tour.id} - {tour.title} ({tour.destination})"):
                submitted, data = tour_form(f"edit_{tour.id}", tour)
                c1, c2 = st.columns(2)
                if submitted:
                    ok, messages = save_tour(data, tour.id)
                    if ok:
                        st.success(messages[0])
                        st.rerun()
                    else:
                        for message in messages:
                            st.error(message)
                if c1.button("Deactivate Package", key=f"deactivate_{tour.id}", use_container_width=True):
                    st.session_state.deactivate_tour_id = tour.id
                if c2.button("Select for Details", key=f"tour_select_{tour.id}", use_container_width=True):
                    st.session_state.admin_selected_tour = tour.id
                if st.session_state.get("deactivate_tour_id") == tour.id:
                    st.warning("Confirm deactivation. The package remains in the database but is hidden from customers.")
                    if st.button("Confirm Deactivate", key=f"confirm_deactivate_{tour.id}", type="primary"):
                        with get_session() as session:
                            row = session.query(TourPackage).filter(TourPackage.id == tour.id).first()
                            row.is_active = False
                        st.session_state.pop("deactivate_tour_id", None)
                        st.success("Package deactivated.")
                        st.rerun()
