from datetime import date

from sqlalchemy.orm import joinedload

from database import get_session
from models import Booking, TourPackage
from utils.validators import validate_future_date


ACTIVE_SEAT_STATUSES = ["Pending Payment", "Confirmed", "Modified"]


def get_active_tours():
    with get_session() as session:
        return (
            session.query(TourPackage)
            .filter(TourPackage.is_active.is_(True))
            .order_by(TourPackage.created_at.desc())
            .all()
        )


def get_tour(tour_id: int):
    with get_session() as session:
        return session.query(TourPackage).filter(TourPackage.id == tour_id).first()


def search_tours(destination="", category="All", min_budget=0, max_budget=None, max_duration=None, available_only=True):
    with get_session() as session:
        query = session.query(TourPackage).filter(TourPackage.is_active.is_(True))
        if destination:
            query = query.filter(TourPackage.destination.ilike(f"%{destination.strip()}%"))
        if category and category != "All":
            query = query.filter(TourPackage.category == category)
        if min_budget:
            query = query.filter(TourPackage.price >= float(min_budget))
        if max_budget:
            query = query.filter(TourPackage.price <= float(max_budget))
        if max_duration:
            query = query.filter(TourPackage.duration_days <= int(max_duration))
        if available_only:
            query = query.filter(TourPackage.available_seats > 0)
        return query.order_by(TourPackage.destination.asc(), TourPackage.price.asc()).all()


def create_booking(user_id: int, tour_id: int, travel_date: date, travelers: int, special_requests: str = ""):
    if not validate_future_date(travel_date):
        return False, "Travel date cannot be in the past.", None
    if travelers <= 0:
        return False, "Travelers must be greater than 0.", None

    with get_session() as session:
        tour = session.query(TourPackage).filter(TourPackage.id == tour_id, TourPackage.is_active.is_(True)).first()
        if not tour:
            return False, "Selected tour package was not found.", None
        if travelers > tour.available_seats:
            return False, f"Only {tour.available_seats} seats are currently available.", None

        booking = Booking(
            user_id=user_id,
            tour_id=tour_id,
            booking_date=date.today(),
            travel_date=travel_date,
            travelers=travelers,
            total_amount=tour.price * travelers,
            status="Pending Payment",
            payment_status="Unpaid",
            special_requests=special_requests.strip(),
        )
        tour.available_seats -= travelers
        session.add(booking)
        session.flush()
        booking_id = booking.id
    return True, "Booking created. Please complete payment.", booking_id


def get_booking(booking_id: int):
    with get_session() as session:
        return (
            session.query(Booking)
            .options(joinedload(Booking.tour), joinedload(Booking.user), joinedload(Booking.payments), joinedload(Booking.resources))
            .filter(Booking.id == booking_id)
            .first()
        )


def get_user_bookings(user_id: int):
    with get_session() as session:
        return (
            session.query(Booking)
            .options(joinedload(Booking.tour), joinedload(Booking.payments), joinedload(Booking.resources))
            .filter(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .all()
        )


def get_all_bookings(status="All", search=""):
    with get_session() as session:
        query = session.query(Booking).options(joinedload(Booking.tour), joinedload(Booking.user), joinedload(Booking.payments))
        if status and status != "All":
            query = query.filter(Booking.status == status)
        rows = query.order_by(Booking.created_at.desc()).all()
        if search:
            needle = search.lower().strip()
            rows = [
                row
                for row in rows
                if needle in str(row.id).lower()
                or needle in row.user.name.lower()
                or needle in row.user.email.lower()
                or needle in row.tour.title.lower()
                or needle in row.tour.destination.lower()
            ]
        return rows


def modify_booking(booking_id: int, travel_date: date, travelers: int, special_requests: str):
    if travelers <= 0:
        return False, "Travelers must be greater than 0."
    if not validate_future_date(travel_date):
        return False, "Travel date cannot be in the past."

    with get_session() as session:
        booking = session.query(Booking).options(joinedload(Booking.tour)).filter(Booking.id == booking_id).first()
        if not booking:
            return False, "Booking was not found."
        if booking.status not in ["Pending Payment", "Confirmed", "Modified"]:
            return False, "This booking cannot be modified."
        seat_difference = travelers - booking.travelers
        if seat_difference > booking.tour.available_seats:
            return False, f"Only {booking.tour.available_seats} additional seats are available."

        previous_total = booking.total_amount
        booking.tour.available_seats -= seat_difference
        booking.travel_date = travel_date
        booking.travelers = travelers
        booking.total_amount = booking.tour.price * travelers
        booking.special_requests = special_requests.strip()
        if booking.payment_status == "Paid" and abs(previous_total - booking.total_amount) > 0.01:
            booking.payment_status = "Unpaid"
            booking.status = "Pending Payment"
        else:
            booking.status = "Modified" if booking.payment_status == "Paid" else "Pending Payment"
    return True, "Booking updated successfully."


def cancel_booking(booking_id: int):
    with get_session() as session:
        booking = session.query(Booking).options(joinedload(Booking.tour), joinedload(Booking.resources)).filter(Booking.id == booking_id).first()
        if not booking:
            return False, "Booking was not found."
        if booking.status in ["Cancelled", "Completed"]:
            return False, "This booking cannot be cancelled."
        booking.tour.available_seats = min(booking.tour.total_seats, booking.tour.available_seats + booking.travelers)
        booking.status = "Cancelled"
        booking.payment_status = "Refunded" if booking.payment_status == "Paid" else booking.payment_status
        for resource in booking.resources:
            resource.status = "Released"
    return True, "Booking cancelled and seats restored."


def update_booking_status(booking_id: int, status: str):
    with get_session() as session:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False, "Booking was not found."
        if booking.status == "Cancelled" and status != "Cancelled":
            return False, "Cancelled bookings cannot be reopened from this screen."
        booking.status = status
    return True, "Booking status updated."
