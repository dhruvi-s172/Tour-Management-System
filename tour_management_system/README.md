# Tour Management System

A complete local Tour Management System built with Python, Streamlit, SQLite, SQLAlchemy, Pandas, Plotly, and Werkzeug password hashing. It is designed as a 5th-semester Software Engineering college project and includes customer workflows, administrator workflows, booking management, simulated payments, resource allocation, reports, and seeded demo data.

## Features

- Customer registration and secure login
- Administrator login with seeded demo admin
- Modern landing page and customer dashboard
- Tour package search and filtering
- Tour details with itinerary and booking information
- Booking creation with availability checks
- Simulated offline payment gateway
- Booking confirmation and downloadable text receipt
- My Bookings with status tracking, modification, and cancellation
- Admin dashboard with KPI cards and Plotly charts
- Tour package add/edit/deactivate management
- Booking search, filtering, details, and status update
- Resource allocation for rooms, vehicles, seats, guides, and meal plans
- Customer activation/deactivation
- Reports with filters, charts, tables, and CSV export
- Role-based authorization and secure logout
- Automatic SQLite database creation and 30+ realistic seeded tour packages

## Technology Stack

- Python 3.11+
- Streamlit
- SQLite
- SQLAlchemy ORM
- Pandas
- Plotly
- Werkzeug password hashing

## Project Structure

```text
tour_management_system/
|-- app.py
|-- auth.py
|-- config.py
|-- database.py
|-- models.py
|-- requirements.txt
|-- README.md
|-- .streamlit/
|   `-- config.toml
|-- pages/
|   |-- customer_dashboard.py
|   |-- search_tours.py
|   |-- tour_details.py
|   |-- booking.py
|   |-- my_bookings.py
|   |-- payment.py
|   |-- admin_dashboard.py
|   |-- manage_tours.py
|   |-- manage_bookings.py
|   |-- manage_resources.py
|   |-- manage_users.py
|   `-- reports.py
|-- services/
|   |-- booking_service.py
|   |-- payment_service.py
|   |-- resource_service.py
|   `-- report_service.py
|-- utils/
|   |-- helpers.py
|   |-- seed_data.py
|   `-- validators.py
|-- data/
|   `-- tour_management.db
`-- assets/
    `-- images/
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## Demo Credentials

Administrator:

```text
Email: admin@tourdemo.com
Password: Admin@123
```

Seeded customer:

```text
Email: customer@example.com
Password: Customer@123
```

You can also register a new customer from the landing page.

## Database Information

The database is created automatically at:

```text
data/tour_management.db
```

Tables:

- USERS
- TOUR_PACKAGES
- BOOKINGS
- PAYMENTS
- RESOURCES

Passwords are stored as hashes using Werkzeug. Plain-text passwords are never stored.

## Customer Workflow

1. Register or log in as a customer.
2. View dashboard metrics and featured packages.
3. Search and filter tour packages.
4. Open tour details.
5. Create a booking by selecting travel date and travelers.
6. Complete payment through the simulated payment gateway.
7. View confirmation and download receipt.
8. Track, modify, or cancel bookings from My Bookings.
9. Log out securely.

## Admin Workflow

1. Log in with the seeded administrator account.
2. Review dashboard KPIs and analytics.
3. Add, edit, or deactivate tour packages.
4. Search and update bookings.
5. Allocate resources to bookings.
6. Activate or deactivate customers.
7. Generate reports and export booking CSV.
8. Log out securely.

## DFD Mapping

- 1.0 Manage Customer: registration, login, activation, deactivation, profile records in USERS.
- 2.0 Manage Tour Packages: add, edit, deactivate, and list packages in TOUR_PACKAGES.
- 3.0 Manage Tour Search: destination, budget, duration, category, and availability filters.
- 4.0 Manage Booking: booking creation, availability check, modification, cancellation, and status tracking in BOOKINGS.
- 5.0 Manage Payment: simulated payment gateway, transaction ID generation, and payment records in PAYMENTS.
- 6.0 Manage Modification, Cancellation & Resources: seat restoration, traveler changes, resource allocation, and RESOURCE records.
- 7.0 Login & Report: role-based login, admin dashboard, analytics, and downloadable reports.

Data stores:

- D1 Customer Data: USERS with role customer.
- D2 Tour Package Data: TOUR_PACKAGES.
- D3 Booking Data: BOOKINGS.
- D4 Payment Data: PAYMENTS.
- D5 Resource & Booking Records: RESOURCES plus booking history.
- D6 User/Admin Data: USERS with role admin and role customer.

## Control Flow Mapping

Customer path:

```text
Start -> Customer Login/Register -> Validate Credentials -> Customer Dashboard
-> Search Tour -> Tour Details -> Availability Check -> Booking
-> Simulated Payment -> Success/Failure -> Confirmation or Retry
-> Booking Status -> Logout -> End
```

Admin path:

```text
Start -> Admin Login -> Validate Credentials -> Admin Dashboard
-> Manage Tours -> Manage Bookings -> Allocate Resources
-> Generate Reports -> Logout -> End
```

## Notes on Payment

The payment gateway is intentionally simulated and works offline. It supports UPI, Credit Card, Debit Card, and Net Banking. The result can be forced to Success or Failed during demonstration, or set to Auto for randomized behavior.

## Future Enhancements

- Real PDF receipt generation
- Email booking confirmations
- Calendar-based availability view
- Advanced cancellation policy and refund tracking
- Admin audit log
- Better image asset management with local uploads
- Unit test suite for services
