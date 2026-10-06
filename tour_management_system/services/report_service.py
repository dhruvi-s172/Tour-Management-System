from datetime import date

import pandas as pd
from sqlalchemy.orm import joinedload

from database import get_session
from models import Booking, TourPackage, User


def dashboard_metrics():
    with get_session() as session:
        total_customers = session.query(User).filter(User.role == "customer").count()
        total_tours = session.query(TourPackage).filter(TourPackage.is_active.is_(True)).count()
        total_bookings = session.query(Booking).count()
        confirmed = session.query(Booking).filter(Booking.status.in_(["Confirmed", "Modified", "Completed"])).count()
        cancelled = session.query(Booking).filter(Booking.status == "Cancelled").count()
        revenue = sum(row.total_amount for row in session.query(Booking).filter(Booking.payment_status == "Paid").all())
        return {
            "total_customers": total_customers,
            "total_tours": total_tours,
            "total_bookings": total_bookings,
            "confirmed": confirmed,
            "cancelled": cancelled,
            "revenue": revenue,
        }


def bookings_dataframe(start_date: date | None = None, end_date: date | None = None, tour_id=None, destination="All", status="All"):
    with get_session() as session:
        query = session.query(Booking).options(joinedload(Booking.tour), joinedload(Booking.user))
        if start_date:
            query = query.filter(Booking.booking_date >= start_date)
        if end_date:
            query = query.filter(Booking.booking_date <= end_date)
        if tour_id and tour_id != "All":
            query = query.filter(Booking.tour_id == int(tour_id))
        if status and status != "All":
            query = query.filter(Booking.status == status)
        rows = query.order_by(Booking.booking_date.desc()).all()

    records = []
    for row in rows:
        if destination != "All" and row.tour.destination != destination:
            continue
        records.append(
            {
                "Booking ID": row.id,
                "Booking Date": row.booking_date,
                "Customer": row.user.name,
                "Email": row.user.email,
                "Tour": row.tour.title,
                "Destination": row.tour.destination,
                "Travel Date": row.travel_date,
                "Travelers": row.travelers,
                "Amount": row.total_amount,
                "Booking Status": row.status,
                "Payment Status": row.payment_status,
            }
        )
    return pd.DataFrame(records)


def chart_frames():
    df = bookings_dataframe()
    if df.empty:
        empty = pd.DataFrame()
        return {
            "monthly_bookings": empty,
            "monthly_revenue": empty,
            "destinations": empty,
            "status": empty,
            "categories": tour_category_dataframe(),
        }
    df["Month"] = pd.to_datetime(df["Booking Date"]).dt.to_period("M").astype(str)
    paid = df[df["Payment Status"] == "Paid"]
    return {
        "monthly_bookings": df.groupby("Month").size().reset_index(name="Bookings"),
        "monthly_revenue": paid.groupby("Month")["Amount"].sum().reset_index(name="Revenue"),
        "destinations": df.groupby("Destination").size().reset_index(name="Bookings").sort_values("Bookings", ascending=False),
        "status": df.groupby("Booking Status").size().reset_index(name="Count"),
        "categories": tour_category_dataframe(),
    }


def tour_category_dataframe():
    with get_session() as session:
        tours = session.query(TourPackage).filter(TourPackage.is_active.is_(True)).all()
    data = [{"Category": tour.category, "Packages": 1} for tour in tours]
    df = pd.DataFrame(data)
    if df.empty:
        return df
    return df.groupby("Category")["Packages"].sum().reset_index()


def report_summary(df: pd.DataFrame):
    if df.empty:
        return {
            "total_bookings": 0,
            "total_revenue": 0,
            "popular_tour": "-",
            "popular_destination": "-",
            "cancelled": 0,
            "customers": 0,
        }
    paid = df[df["Payment Status"] == "Paid"]
    return {
        "total_bookings": len(df),
        "total_revenue": paid["Amount"].sum() if not paid.empty else 0,
        "popular_tour": df["Tour"].mode().iloc[0] if not df["Tour"].mode().empty else "-",
        "popular_destination": df["Destination"].mode().iloc[0] if not df["Destination"].mode().empty else "-",
        "cancelled": int((df["Booking Status"] == "Cancelled").sum()),
        "customers": df["Email"].nunique(),
    }
