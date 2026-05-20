from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), default='user', nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    emergency_contact = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship('Vehicle', backref='owner', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='owner', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', lazy=True)
    sos_alerts = db.relationship('SOSAlert', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Garage(db.Model):
    __tablename__ = 'garages'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    latitude = db.Column(db.Float, nullable=False, default=19.0760)
    longitude = db.Column(db.Float, nullable=False, default=72.8777)
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    open_time = db.Column(db.String(10), default='09:00')
    close_time = db.Column(db.String(10), default='20:00')
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship('User', backref='garage', uselist=False)
    services = db.relationship('Service', backref='garage', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='garage', lazy=True)
    sos_alerts = db.relationship('SOSAlert', backref='garage', lazy=True)

    def __repr__(self):
        return f'<Garage {self.name}>'


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    garage_id = db.Column(db.Integer, db.ForeignKey('garages.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='service', lazy=True)

    def __repr__(self):
        return f'<Service {self.name}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    garage_id = db.Column(db.Integer, db.ForeignKey('garages.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'rejected', 'completed', 'cancelled'),
                       default='pending', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reg_number = db.Column(db.String(20), nullable=False)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    color = db.Column(db.String(40), nullable=True)
    insurance_number = db.Column(db.String(80), nullable=True)
    insurance_expiry = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.reg_number}>'


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doc_type = db.Column(db.Enum('RC', 'Insurance', 'License', 'Other'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.String(300), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.doc_type} - {self.original_name}>'


class SOSAlert(db.Model):
    __tablename__ = 'sos_alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    garage_id = db.Column(db.Integer, db.ForeignKey('garages.id'), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(300), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('active', 'acknowledged', 'resolved'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<SOSAlert {self.id} - {self.status}>'
