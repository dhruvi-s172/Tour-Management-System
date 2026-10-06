from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(String(30), nullable=False, default="customer")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="user")


class TourPackage(Base):
    __tablename__ = "tour_packages"

    id = Column(Integer, primary_key=True)
    title = Column(String(180), nullable=False)
    destination = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    itinerary = Column(Text, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    available_seats = Column(Integer, nullable=False)
    total_seats = Column(Integer, nullable=False)
    category = Column(String(80), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="tour")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tour_packages.id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    travel_date = Column(Date, nullable=False)
    travelers = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="Pending Payment")
    payment_status = Column(String(50), nullable=False, default="Unpaid")
    special_requests = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    tour = relationship("TourPackage", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    resources = relationship("Resource", back_populates="booking")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    transaction_id = Column(String(80), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(60), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), nullable=False)

    booking = relationship("Booking", back_populates="payments")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    resource_type = Column(String(80), nullable=False)
    resource_name = Column(String(120), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="Allocated")

    booking = relationship("Booking", back_populates="resources")
