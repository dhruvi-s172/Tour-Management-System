import streamlit as st

from auth import login_user, logout_user, register_customer, set_current_user
from config import ADMIN_EMAIL, ADMIN_PASSWORD, APP_NAME, ROLES
from database import init_db
from pages import (
    admin_dashboard,
    booking,
    customer_dashboard,
    manage_bookings,
    manage_resources,
    manage_tours,
    manage_users,
    my_bookings,
    payment,
    reports,
    search_tours,
    tour_details,
)
from services.booking_service import get_active_tours
from utils.helpers import inject_css, tour_card
from utils.seed_data import seed_database


st.set_page_config(
    page_title=APP_NAME,
    page_icon=":airplane:",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()
seed_database()
inject_css()


def set_page(page: str):
    st.session_state.page = page
    st.rerun()


def init_session():
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("authenticated", False)


def sidebar_navigation():
    with st.sidebar:
        st.markdown("<div class='nav-title'>Tour Management System</div>", unsafe_allow_html=True)
        user = st.session_state.get("user")
        if user:
            st.caption(f"Signed in as {user['name']}")
            st.caption(user["role"].title())

        if not st.session_state.get("authenticated"):
            options = ["Home", "Login", "Register", "Admin Login"]
            current = st.session_state.get("page", "Home")
            default_index = options.index(current) if current in options else 0
            selected = st.radio("Open Section", options, index=default_index)
            if selected != current:
                set_page(selected)
            st.markdown("---")
            st.caption("Demo admin")
            st.caption(ADMIN_EMAIL)
        elif user["role"] == ROLES["CUSTOMER"]:
            options = ["Customer Dashboard", "Search Tours", "My Bookings"]
            current = st.session_state.get("page", "Customer Dashboard")
            default_index = options.index(current) if current in options else 0
            selected = st.radio("Customer Sections", options, index=default_index)
            if (current in options and selected != current) or (current not in options and selected != options[default_index]):
                set_page(selected)
            if current not in options:
                st.caption(f"Current workflow: {current}")
            if st.button("Logout", use_container_width=True):
                logout_user()
                st.rerun()
        elif user["role"] == ROLES["ADMIN"]:
            options = ["Admin Dashboard", "Manage Tours", "Manage Bookings", "Manage Resources", "Manage Users", "Reports"]
            current = st.session_state.get("page", "Admin Dashboard")
            default_index = options.index(current) if current in options else 0
            selected = st.radio("Admin Sections", options, index=default_index)
            if selected != current:
                set_page(selected)
            if st.button("Logout", use_container_width=True):
                logout_user()
                st.rerun()


def home_page():
    st.markdown(
        """
        <section class='hero'>
            <h1>Explore. Book. Travel.</h1>
            <p>Plan your perfect journey with smart and seamless tour management.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h2 class='section-title'>Popular Tour Packages</h2>", unsafe_allow_html=True)
    tours = get_active_tours()[:9]
    for row_start in range(0, len(tours), 3):
        cols = st.columns(3)
        for col, tour in zip(cols, tours[row_start : row_start + 3]):
            with col:
                tour_card(tour, f"home_{row_start}")

    st.markdown("<h2 class='section-title'>Featured Travel Styles</h2>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='tm-card'><h3>Weekend Escapes</h3><p class='muted'>Short, budget-friendly trips for quick college demos and easy booking flows.</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='tm-card'><h3>Adventure Trails</h3><p class='muted'>High-energy tours with vehicle, guide, and seat resource allocation.</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='tm-card'><h3>Luxury Retreats</h3><p class='muted'>Premium packages with higher revenue impact for admin analytics.</p></div>", unsafe_allow_html=True)
    c4.markdown("<div class='tm-card'><h3>International Plans</h3><p class='muted'>Presentation-ready packages with richer pricing and report filters.</p></div>", unsafe_allow_html=True)

    st.markdown("<h2 class='section-title'>Get Started</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Customer Login", type="primary", use_container_width=True):
        set_page("Login")
    if c2.button("Create Customer Account", use_container_width=True):
        set_page("Register")
    if c3.button("Administrator Login", use_container_width=True):
        set_page("Admin Login")


def login_page(expected_role=ROLES["CUSTOMER"]):
    title = "Administrator Login" if expected_role == ROLES["ADMIN"] else "Customer Login"
    st.title(title)
    if expected_role == ROLES["ADMIN"]:
        st.info(f"Demo credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    with st.form(f"{expected_role}_login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
    if submitted:
        ok, message, user = login_user(email, password, expected_role=expected_role)
        if ok:
            set_current_user(user)
            st.success(message)
            st.rerun()
        else:
            st.error(message)


def register_page():
    st.title("Create Customer Account")
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
    if submitted:
        ok, messages = register_customer(name, email, phone, password, confirm)
        if ok:
            st.success(messages[0])
            if st.button("Go to Login", use_container_width=True):
                set_page("Login")
        else:
            for message in messages:
                st.error(message)


def route():
    page = st.session_state.get("page", "Home")
    public_pages = {
        "Home": home_page,
        "Login": lambda: login_page(ROLES["CUSTOMER"]),
        "Register": register_page,
        "Admin Login": lambda: login_page(ROLES["ADMIN"]),
    }
    customer_pages = {
        "Customer Dashboard": customer_dashboard.render,
        "Search Tours": search_tours.render,
        "Tour Details": tour_details.render,
        "Booking": booking.render,
        "Payment": payment.render,
        "My Bookings": my_bookings.render,
    }
    admin_pages = {
        "Admin Dashboard": admin_dashboard.render,
        "Manage Tours": manage_tours.render,
        "Manage Bookings": manage_bookings.render,
        "Manage Resources": manage_resources.render,
        "Manage Users": manage_users.render,
        "Reports": reports.render,
    }
    if page in public_pages:
        public_pages[page]()
    elif page in customer_pages:
        customer_pages[page]()
    elif page in admin_pages:
        admin_pages[page]()
    else:
        st.session_state.page = "Home"
        home_page()


init_session()
sidebar_navigation()
route()
