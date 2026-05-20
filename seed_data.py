"""
seed_data.py — Run this ONCE after setting up the DB to populate demo data.
Usage: python seed_data.py
"""
from run import app
from app import db
from app.models.models import User, Garage, Service

with app.app_context():
    db.create_all()

    # ── Demo Admin / Garage ──────────────────────────────────────────────
    if not User.query.filter_by(email='admin@garage.com').first():
        admin = User(name='Rajesh Auto Works', email='admin@garage.com',
                     phone='9876543210', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()

        garage = Garage(
            admin_id=admin.id,
            name='Rajesh Auto Works',
            address='Shop No 5, SV Road',
            city='Mumbai',
            phone='9876543210',
            latitude=19.0760, longitude=72.8777,
            rating=4.5, total_ratings=28,
            description='Trusted multi-brand car service centre since 2008.'
        )
        db.session.add(garage)
        db.session.flush()

        services = [
            Service(garage_id=garage.id, name='Oil Change',        price=499,  duration_minutes=30,  description='Engine oil + filter replacement'),
            Service(garage_id=garage.id, name='Full Car Service',  price=1999, duration_minutes=120, description='Complete 50-point inspection & service'),
            Service(garage_id=garage.id, name='Tyre Replacement',  price=799,  duration_minutes=45,  description='Per tyre, balancing included'),
            Service(garage_id=garage.id, name='AC Service',        price=1299, duration_minutes=90,  description='Gas recharge, cleaning & check'),
            Service(garage_id=garage.id, name='Battery Replacement',price=3499,duration_minutes=30,  description='MRP battery with 2-yr warranty'),
            Service(garage_id=garage.id, name='Wheel Alignment',   price=599,  duration_minutes=60,  description='4-wheel computerised alignment'),
        ]
        db.session.add_all(services)

    # ── Second Demo Garage ───────────────────────────────────────────────
    if not User.query.filter_by(email='admin2@garage.com').first():
        admin2 = User(name='City Motors', email='admin2@garage.com',
                      phone='9988776655', role='admin')
        admin2.set_password('admin123')
        db.session.add(admin2)
        db.session.flush()

        garage2 = Garage(
            admin_id=admin2.id,
            name='City Motors Service Center',
            address='Plot 12, Andheri East',
            city='Mumbai',
            phone='9988776655',
            latitude=19.1136, longitude=72.8697,
            rating=4.2, total_ratings=15,
            description='Specialised in Maruti, Hyundai & Honda cars.'
        )
        db.session.add(garage2)
        db.session.flush()

        db.session.add_all([
            Service(garage_id=garage2.id, name='Denting & Painting', price=2499, duration_minutes=180, description='Per panel, OEM paints used'),
            Service(garage_id=garage2.id, name='Engine Repair',       price=4999, duration_minutes=240, description='Diagnosis + repair, parts extra'),
            Service(garage_id=garage2.id, name='Brake Service',       price=899,  duration_minutes=60,  description='Pads, shoes & fluid check'),
        ])

    # ── Demo Customer ────────────────────────────────────────────────────
    if not User.query.filter_by(email='user@example.com').first():
        user = User(name='Arjun Sharma', email='user@example.com',
                    phone='9123456780', role='user',
                    latitude=19.0825, longitude=72.8875,
                    emergency_contact='Priya Sharma - 9000011112')
        user.set_password('user123')
        db.session.add(user)

    db.session.commit()
    print("✅ Seed data inserted successfully!")
    print("\n📋 Login Credentials:")
    print("  Customer  → user@example.com   / user123")
    print("  Admin #1  → admin@garage.com   / admin123")
    print("  Admin #2  → admin2@garage.com  / admin123")
