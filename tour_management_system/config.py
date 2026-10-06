from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "tour_management.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

APP_NAME = "Tour Management System"
ADMIN_EMAIL = "admin@tourdemo.com"
ADMIN_PASSWORD = "Admin@123"

ROLES = {
    "CUSTOMER": "customer",
    "ADMIN": "admin",
}

TOUR_CATEGORIES = [
    "Adventure",
    "Beach",
    "Heritage",
    "Family",
    "Honeymoon",
    "Nature",
    "International",
]

BOOKING_STATUSES = [
    "Pending Payment",
    "Confirmed",
    "Modified",
    "Cancelled",
    "Completed",
]

PAYMENT_STATUSES = ["Unpaid", "Paid", "Failed", "Refunded"]

RESOURCE_TYPES = ["Hotel Room", "Vehicle", "Seat", "Guide", "Meal Plan"]
