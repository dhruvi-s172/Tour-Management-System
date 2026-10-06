import re
from datetime import date


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN = re.compile(r"^[0-9+\-\s]{7,15}$")


def validate_email(email: str) -> bool:
    return bool(email and EMAIL_PATTERN.match(email.strip()))


def validate_phone(phone: str) -> bool:
    return bool(phone and PHONE_PATTERN.match(phone.strip()))


def validate_password(password: str):
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def validate_future_date(value: date) -> bool:
    return value >= date.today()


def validate_positive_number(value, field_name: str):
    try:
        if float(value) <= 0:
            return False, f"{field_name} must be greater than 0."
    except (TypeError, ValueError):
        return False, f"{field_name} must be a number."
    return True, ""


def validate_non_negative_int(value, field_name: str):
    try:
        if int(value) < 0:
            return False, f"{field_name} cannot be negative."
    except (TypeError, ValueError):
        return False, f"{field_name} must be a whole number."
    return True, ""
