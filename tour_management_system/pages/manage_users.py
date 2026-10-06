import pandas as pd
import streamlit as st

from auth import require_role
from config import ROLES
from database import get_session
from models import User


def render():
    if not require_role(ROLES["ADMIN"]):
        return
    st.title("User Management")
    search = st.text_input("Search customers", placeholder="Name, email, or phone")

    with get_session() as session:
        customers = session.query(User).filter(User.role == ROLES["CUSTOMER"]).order_by(User.created_at.desc()).all()
    if search:
        needle = search.lower().strip()
        customers = [c for c in customers if needle in c.name.lower() or needle in c.email.lower() or needle in c.phone.lower()]

    if customers:
        df = pd.DataFrame(
            [
                {
                    "ID": c.id,
                    "Name": c.name,
                    "Email": c.email,
                    "Phone": c.phone,
                    "Registered": c.created_at.strftime("%d %b %Y"),
                    "Active": c.is_active,
                }
                for c in customers
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
        selected = st.selectbox("Select Customer", customers, format_func=lambda c: f"{c.name} - {c.email}")
        action = "Deactivate" if selected.is_active else "Activate"
        if st.button(f"{action} Customer", type="primary", use_container_width=True):
            with get_session() as session:
                row = session.query(User).filter(User.id == selected.id).first()
                row.is_active = not row.is_active
            st.success(f"Customer {action.lower()}d.")
            st.rerun()
    else:
        st.info("No customers found.")
