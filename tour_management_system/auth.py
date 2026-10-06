import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash

from config import ROLES
from database import get_session
from models import User
from utils.validators import validate_email, validate_password, validate_phone


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def register_customer(name: str, email: str, phone: str, password: str, confirm_password: str):
    errors = []
    if not name.strip():
        errors.append("Full name is required.")
    if not validate_email(email):
        errors.append("Enter a valid email address.")
    if not validate_phone(phone):
        errors.append("Enter a valid phone number.")
    ok_password, password_message = validate_password(password)
    if not ok_password:
        errors.append(password_message)
    if password != confirm_password:
        errors.append("Password and confirm password must match.")
    if errors:
        return False, errors

    with get_session() as session:
        existing = session.query(User).filter(User.email == email.lower().strip()).first()
        if existing:
            return False, ["An account with this email already exists."]
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            phone=phone.strip(),
            password_hash=hash_password(password),
            role=ROLES["CUSTOMER"],
            is_active=True,
        )
        session.add(user)
    return True, ["Registration successful. Please log in to continue."]


def login_user(email: str, password: str, expected_role: str | None = None):
    with get_session() as session:
        user = session.query(User).filter(User.email == email.lower().strip()).first()
        if not user or not verify_password(password, user.password_hash):
            return False, "Invalid email or password.", None
        if not user.is_active:
            return False, "This account is inactive. Please contact the administrator.", None
        if expected_role and user.role != expected_role:
            return False, "This login area is not available for your account role.", None
        return True, "Login successful.", {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
        }


def set_current_user(user_data: dict):
    st.session_state.user = user_data
    st.session_state.authenticated = True
    st.session_state.role = user_data["role"]
    st.session_state.page = "Customer Dashboard" if user_data["role"] == ROLES["CUSTOMER"] else "Admin Dashboard"


def logout_user():
    for key in [
        "user",
        "authenticated",
        "role",
        "page",
        "selected_tour_id",
        "selected_booking_id",
        "payment_booking_id",
    ]:
        st.session_state.pop(key, None)
    st.session_state.page = "Home"


def current_user():
    return st.session_state.get("user")


def require_role(role: str) -> bool:
    user = current_user()
    if not st.session_state.get("authenticated") or not user or user.get("role") != role:
        st.error("Access Denied")
        if role == ROLES["ADMIN"]:
            st.session_state.page = "Admin Login"
        else:
            st.session_state.page = "Login"
        return False
    return True
