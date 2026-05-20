# 🔧 Smart Garage Locator System

A full-stack Flask web application for locating nearby garages, booking services,
managing vehicles/documents, and sending emergency SOS alerts.

---

## 📁 Project Structure

```
smart_garage_locator/
├── run.py                   ← Flask entry point
├── seed_data.py             ← Demo data seeder
├── requirements.txt
├── .env                     ← Environment variables
├── config/
│   └── config.py
├── app/
│   ├── __init__.py          ← Flask factory
│   ├── models/
│   │   └── models.py        ← All DB models (7 tables)
│   ├── routes/
│   │   ├── auth.py          ← Login, Register, Logout
│   │   ├── user.py          ← Customer features
│   │   └── admin.py         ← Garage admin panel
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/            ← login.html, register.html
│   │   ├── user/            ← dashboard, garages, booking, vehicles, docs, sos, profile
│   │   └── admin/           ← dashboard, garage_profile, services, bookings, sos_alerts, customers
│   └── static/
│       └── uploads/         ← Uploaded documents
└── docs/
    └── schema.sql           ← MySQL CREATE TABLE statements
```

---

## 🚀 Quick Start (SQLite — No MySQL needed)

```bash
# 1. Clone / unzip project
cd smart_garage_locator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed demo data & start server
python seed_data.py
python run.py
```

Open → **http://localhost:5000**

---

## 🔐 Demo Login Credentials

| Role        | Email                | Password  |
|-------------|----------------------|-----------|
| Customer    | user@example.com     | user123   |
| Garage Admin| admin@garage.com     | admin123  |
| Garage Admin| admin2@garage.com    | admin123  |

---

## 🗄️ MySQL Setup (Optional)

```bash
# 1. Create database
mysql -u root -p < docs/schema.sql

# 2. Update .env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/smart_garage_db

# 3. Run
python run.py
```

---

## ✨ Features

### Customer (User)
- 📍 **Find Garages** — sorted by distance using Haversine formula
- 📅 **Book Services** — choose service, vehicle, date & time
- 🚗 **Vehicle Management** — add/remove vehicles with insurance info
- 📁 **Document Storage** — upload RC, Insurance, License (PDF/image)
- 🚨 **Emergency SOS** — one-click alert to nearest garage
- 👤 **Profile** — update contact & location

### Garage Admin
- 🏪 **Garage Profile** — name, address, location, hours
- 🔧 **Services CRUD** — add/edit/delete services with pricing
- 📋 **Booking Management** — confirm / reject / mark complete
- 👥 **Customer List** — view all customers who booked
- 🚨 **SOS Alerts** — view & resolve emergency alerts

---

## 🗃️ Database Schema (7 Tables)

```
users ──┬── garages ──┬── services ──── bookings
        │             └── sos_alerts        │
        ├── vehicles ────────────────────────┘
        ├── documents
        └── bookings
```

---

## ⚙️ Environment Variables (.env)

| Variable            | Description                        |
|---------------------|------------------------------------|
| SECRET_KEY          | Flask session secret key           |
| DATABASE_URL        | DB connection string               |
| GOOGLE_MAPS_API_KEY | For Google Maps integration        |
| UPLOAD_FOLDER       | Path for uploaded files            |

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.11+, Flask 3.x           |
| Database  | SQLite (dev) / MySQL (prod)       |
| ORM       | SQLAlchemy + Flask-Migrate        |
| Auth      | Flask-Login                       |
| Frontend  | Bootstrap 5.3, Font Awesome 6     |
| Location  | Haversine formula, HTML5 Geoloc   |
