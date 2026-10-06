import pandas as pd
import streamlit as st

from auth import require_role
from config import RESOURCE_TYPES, ROLES
from services.booking_service import get_all_bookings
from services.resource_service import RESOURCE_LIMITS, allocate_resource, get_resources, resource_summary, update_resource_status


def render():
    if not require_role(ROLES["ADMIN"]):
        return
    st.title("Resource Allocation")

    summary = resource_summary()
    cols = st.columns(len(RESOURCE_TYPES))
    for col, resource_type in zip(cols, RESOURCE_TYPES):
        col.metric(resource_type, f"{summary.get(resource_type, 0)}/{RESOURCE_LIMITS.get(resource_type, 9999)}")

    st.markdown("### Allocate Resource")
    eligible_bookings = [b for b in get_all_bookings() if b.status in ["Confirmed", "Modified", "Pending Payment"]]
    if not eligible_bookings:
        st.info("No eligible bookings for resource allocation.")
    else:
        with st.form("resource_form"):
            booking = st.selectbox("Booking", eligible_bookings, format_func=lambda b: f"#{b.id} - {b.user.name} - {b.tour.title}")
            resource_type = st.selectbox("Resource Type", RESOURCE_TYPES)
            resource_name = st.text_input("Resource Name", placeholder="Example: Hotel Pearl Room Block")
            quantity = st.number_input("Quantity", min_value=1, value=1)
            submitted = st.form_submit_button("Allocate", type="primary", use_container_width=True)
        if submitted:
            if not resource_name.strip():
                st.error("Resource name is required.")
            else:
                ok, message = allocate_resource(booking.id, resource_type, resource_name, quantity)
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("### Allocated Resources")
    resources = get_resources()
    if resources:
        df = pd.DataFrame(
            [
                {
                    "ID": r.id,
                    "Booking ID": r.booking_id,
                    "Type": r.resource_type,
                    "Name": r.resource_name,
                    "Quantity": r.quantity,
                    "Status": r.status,
                }
                for r in resources
            ]
        )
        st.dataframe(df, hide_index=True, use_container_width=True)
        selected = st.selectbox("Update Resource Status", resources, format_func=lambda r: f"{r.id} - {r.resource_type} - {r.resource_name}")
        new_status = st.selectbox("Status", ["Allocated", "Released", "Completed"])
        if st.button("Save Resource Status", use_container_width=True):
            ok, message = update_resource_status(selected.id, new_status)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("No resources allocated yet.")
