from collections import defaultdict

from database import get_session
from models import Booking, Resource


RESOURCE_LIMITS = {
    "Hotel Room": 80,
    "Vehicle": 25,
    "Seat": 600,
    "Guide": 20,
    "Meal Plan": 500,
}


def get_allocated_quantity(resource_type: str, exclude_resource_id: int | None = None):
    with get_session() as session:
        query = session.query(Resource).filter(Resource.resource_type == resource_type, Resource.status == "Allocated")
        if exclude_resource_id:
            query = query.filter(Resource.id != exclude_resource_id)
        return sum(row.quantity for row in query.all())


def can_allocate(resource_type: str, quantity: int, exclude_resource_id: int | None = None):
    if quantity <= 0:
        return False, "Quantity must be greater than 0."
    limit = RESOURCE_LIMITS.get(resource_type, 9999)
    allocated = get_allocated_quantity(resource_type, exclude_resource_id)
    if allocated + quantity > limit:
        return False, f"Only {max(0, limit - allocated)} {resource_type} units are available."
    return True, ""


def allocate_resource(booking_id: int, resource_type: str, resource_name: str, quantity: int):
    ok, message = can_allocate(resource_type, quantity)
    if not ok:
        return False, message
    with get_session() as session:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False, "Booking was not found."
        if booking.status == "Cancelled":
            return False, "Resources cannot be allocated to cancelled bookings."
        resource = Resource(
            booking_id=booking_id,
            resource_type=resource_type,
            resource_name=resource_name.strip(),
            quantity=quantity,
            status="Allocated",
        )
        session.add(resource)
    return True, "Resource allocated successfully."


def update_resource_status(resource_id: int, status: str):
    with get_session() as session:
        resource = session.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            return False, "Resource was not found."
        resource.status = status
    return True, "Resource status updated."


def get_resources():
    with get_session() as session:
        return session.query(Resource).order_by(Resource.id.desc()).all()


def resource_summary():
    resources = get_resources()
    totals = defaultdict(int)
    for resource in resources:
        if resource.status == "Allocated":
            totals[resource.resource_type] += resource.quantity
    return dict(totals)
