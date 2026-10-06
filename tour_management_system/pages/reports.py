from datetime import date, timedelta

import plotly.express as px
import streamlit as st

from auth import require_role
from config import BOOKING_STATUSES, ROLES
from database import get_session
from models import TourPackage
from services.report_service import bookings_dataframe, report_summary
from utils.helpers import dataframe_download, metric_card, money


def render():
    if not require_role(ROLES["ADMIN"]):
        return
    st.title("Reports")
    with get_session() as session:
        tours = session.query(TourPackage).order_by(TourPackage.title.asc()).all()
        destinations = sorted({tour.destination for tour in tours})

    c1, c2, c3, c4 = st.columns(4)
    start_date = c1.date_input("Start Date", value=date.today() - timedelta(days=90))
    end_date = c2.date_input("End Date", value=date.today())
    tour_choice = c3.selectbox("Tour", ["All"] + tours, format_func=lambda t: "All" if t == "All" else t.title)
    destination = c4.selectbox("Destination", ["All"] + destinations)
    status = st.selectbox("Booking Status", ["All"] + BOOKING_STATUSES)
    tour_id = "All" if tour_choice == "All" else tour_choice.id

    df = bookings_dataframe(start_date, end_date, tour_id, destination, status)
    summary = report_summary(df)
    cols = st.columns(6)
    with cols[0]:
        metric_card("Bookings", summary["total_bookings"])
    with cols[1]:
        metric_card("Revenue", money(summary["total_revenue"]))
    with cols[2]:
        metric_card("Popular Tour", summary["popular_tour"])
    with cols[3]:
        metric_card("Top Destination", summary["popular_destination"])
    with cols[4]:
        metric_card("Cancelled", summary["cancelled"])
    with cols[5]:
        metric_card("Customers", summary["customers"])

    if df.empty:
        st.info("No report data for selected filters.")
        return
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(px.bar(df.groupby("Destination").size().reset_index(name="Bookings"), x="Destination", y="Bookings", title="Bookings by Destination"), use_container_width=True)
    with c6:
        st.plotly_chart(px.pie(df.groupby("Booking Status").size().reset_index(name="Count"), names="Booking Status", values="Count", title="Status Mix"), use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    dataframe_download(df, "Download Booking Report", "booking_report.csv")
