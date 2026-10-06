import plotly.express as px
import streamlit as st

from auth import require_role
from config import ROLES
from services.report_service import chart_frames, dashboard_metrics
from utils.helpers import metric_card, money


def render():
    if not require_role(ROLES["ADMIN"]):
        return
    st.title("Admin Dashboard")
    metrics = dashboard_metrics()
    cols = st.columns(6)
    with cols[0]:
        metric_card("Customers", metrics["total_customers"])
    with cols[1]:
        metric_card("Packages", metrics["total_tours"])
    with cols[2]:
        metric_card("Bookings", metrics["total_bookings"])
    with cols[3]:
        metric_card("Confirmed", metrics["confirmed"])
    with cols[4]:
        metric_card("Cancelled", metrics["cancelled"])
    with cols[5]:
        metric_card("Revenue", money(metrics["revenue"]))

    frames = chart_frames()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(frames["monthly_bookings"], x="Month", y="Bookings", title="Bookings by Month"), use_container_width=True)
    with c2:
        st.plotly_chart(px.line(frames["monthly_revenue"], x="Month", y="Revenue", markers=True, title="Revenue by Month"), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(px.bar(frames["destinations"], x="Destination", y="Bookings", title="Popular Destinations"), use_container_width=True)
    with c4:
        st.plotly_chart(px.pie(frames["status"], names="Booking Status", values="Count", title="Booking Status Distribution"), use_container_width=True)
    st.plotly_chart(px.pie(frames["categories"], names="Category", values="Packages", title="Tour Category Distribution"), use_container_width=True)
