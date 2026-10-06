from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st


def money(value) -> str:
    return f"Rs. {float(value):,.0f}"


def fmt_date(value) -> str:
    if not value:
        return "-"
    if isinstance(value, str):
        return value
    return value.strftime("%d %b %Y")


def status_badge(status: str) -> str:
    color_map = {
        "Confirmed": ("#dcfce7", "#166534"),
        "Modified": ("#dbeafe", "#1d4ed8"),
        "Pending Payment": ("#fef3c7", "#92400e"),
        "Cancelled": ("#fee2e2", "#991b1b"),
        "Completed": ("#e0e7ff", "#3730a3"),
        "Paid": ("#dcfce7", "#166534"),
        "Unpaid": ("#fef3c7", "#92400e"),
        "Failed": ("#fee2e2", "#991b1b"),
        "Allocated": ("#dbeafe", "#1d4ed8"),
    }
    bg, fg = color_map.get(status, ("#e5e7eb", "#374151"))
    return f"<span class='badge' style='background:{bg}; color:{fg};'>{escape(status)}</span>"


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: Inter, system-ui, -apple-system, Segoe UI, sans-serif; }
        .main .block-container { padding-top: 1.2rem; max-width: 1220px; }
        h1, h2, h3 { letter-spacing: 0; color: #172033; }
        div[data-testid="stSidebar"] { background: #071827; }
        div[data-testid="stSidebar"] * { color: #f8fafc; }
        .hero {
            min-height: 430px;
            border-radius: 0;
            padding: 3.5rem 3rem;
            color: white;
            background:
                linear-gradient(90deg, rgba(7,24,39,.94), rgba(15,118,110,.78), rgba(251,146,60,.20)),
                url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80');
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .hero h1 { color: white; font-size: clamp(2.6rem, 5vw, 4.7rem); line-height: 1; margin-bottom: .8rem; }
        .hero p { max-width: 620px; color: #e2e8f0; font-size: 1.12rem; }
        .section-title { margin-top: 1.5rem; margin-bottom: .75rem; }
        .tm-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.05rem;
            box-shadow: 0 10px 26px rgba(15, 23, 42, .06);
            height: 100%;
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 5px solid #0f766e;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, .05);
        }
        .metric-card .label { color: #64748b; font-size: .86rem; font-weight: 600; }
        .metric-card .value { color: #0f172a; font-size: 1.65rem; font-weight: 800; margin-top: .15rem; }
        .tour-img {
            width: 100%;
            height: 170px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            background: #e5e7eb;
        }
        .detail-img {
            width: 100%;
            max-height: 420px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        .badge {
            display: inline-block;
            padding: .28rem .58rem;
            border-radius: 999px;
            font-size: .78rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .muted { color: #64748b; }
        .tiny { font-size: .82rem; }
        .price { color: #ea580c; font-weight: 800; font-size: 1.12rem; }
        .nav-title { font-weight: 800; font-size: 1.1rem; padding: .4rem 0 1rem; color: white; }
        .status-flow {
            display: flex;
            gap: .7rem;
            flex-wrap: wrap;
            align-items: center;
            margin: .6rem 0 1rem;
        }
        .status-step {
            border: 1px solid #cbd5e1;
            border-radius: 999px;
            padding: .45rem .75rem;
            font-weight: 700;
            font-size: .82rem;
            background: white;
        }
        .status-step.active { background: #0f766e; color: white; border-color: #0f766e; }
        .status-step.cancelled { background: #dc2626; color: white; border-color: #dc2626; }
        .dataframe tbody tr:hover { background: #f8fafc; }
        button[kind="primary"] { background: #0f766e !important; border-color: #0f766e !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str):
    st.markdown(
        f"<div class='metric-card'><div class='label'>{escape(label)}</div><div class='value'>{escape(str(value))}</div></div>",
        unsafe_allow_html=True,
    )


def tour_card(tour, key_prefix: str, show_buttons=True):
    st.markdown(
        f"""
        <div class='tm-card'>
            <img class='tour-img' src='{escape(tour.image_url or "")}' onerror="this.style.display='none'">
            <h3 style='margin:.75rem 0 .25rem'>{escape(tour.title)}</h3>
            <div class='muted'>{escape(tour.destination)} | {tour.duration_days} days | {escape(tour.category)}</div>
            <p class='tiny'>{escape(tour.description[:120])}...</p>
            <div class='price'>{money(tour.price)} per person</div>
            <div class='tiny muted'>{tour.available_seats} of {tour.total_seats} seats available</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if show_buttons:
        cols = st.columns(2)
        if cols[0].button("View Details", key=f"{key_prefix}_details_{tour.id}", use_container_width=True):
            st.session_state.selected_tour_id = tour.id
            st.session_state.page = "Tour Details"
            st.rerun()
        if cols[1].button("Book Now", key=f"{key_prefix}_book_{tour.id}", type="primary", use_container_width=True):
            st.session_state.selected_tour_id = tour.id
            st.session_state.page = "Booking"
            st.rerun()


def dataframe_download(df: pd.DataFrame, label: str, filename: str):
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def receipt_text(booking, payment=None) -> str:
    transaction_id = payment.transaction_id if payment else "-"
    paid_on = fmt_date(payment.payment_date) if payment else "-"
    return f"""TOUR MANAGEMENT SYSTEM - BOOKING RECEIPT
Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}

Booking ID: {booking.id}
Customer: {booking.user.name}
Tour: {booking.tour.title}
Destination: {booking.tour.destination}
Travel Date: {fmt_date(booking.travel_date)}
Travelers: {booking.travelers}
Total Amount: {money(booking.total_amount)}
Booking Status: {booking.status}
Payment Status: {booking.payment_status}
Transaction ID: {transaction_id}
Payment Date: {paid_on}

This receipt is generated by the offline simulated payment gateway for academic demonstration.
"""
