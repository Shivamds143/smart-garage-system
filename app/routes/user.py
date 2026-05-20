from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Garage, Service, Booking, Vehicle, Document, SOSAlert
from datetime import datetime, date
import os, uuid, math

user_bp = Blueprint('user', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * 2 * math.asin(math.sqrt(a)), 2)


@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'user':
        return redirect(url_for('admin.dashboard'))
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).limit(5).all()
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    sos_alerts = SOSAlert.query.filter_by(user_id=current_user.id).order_by(SOSAlert.created_at.desc()).limit(3).all()
    return render_template('user/dashboard.html', bookings=bookings, vehicles=vehicles, sos_alerts=sos_alerts)


@user_bp.route('/garages')
@login_required
def garages():
    lat = request.args.get('lat', type=float) or current_user.latitude or 19.0760
    lon = request.args.get('lon', type=float) or current_user.longitude or 72.8777
    all_garages = Garage.query.filter_by(is_active=True).all()
    garage_list = []
    for g in all_garages:
        dist = haversine(lat, lon, g.latitude, g.longitude)
        garage_list.append({'garage': g, 'distance': dist})
    garage_list.sort(key=lambda x: x['distance'])
    return render_template('user/garages.html', garages=garage_list, user_lat=lat, user_lon=lon)


@user_bp.route('/garage/<int:garage_id>')
@login_required
def garage_detail(garage_id):
    garage = Garage.query.get_or_404(garage_id)
    services = Service.query.filter_by(garage_id=garage_id, is_available=True).all()
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    return render_template('user/garage_detail.html', garage=garage, services=services, vehicles=vehicles)


@user_bp.route('/book', methods=['POST'])
# @login_required
# def book_service():
#     garage_id = request.form.get('garage_id', type=int)
#     service_id = request.form.get('service_id', type=int)
#     vehicle_id = request.form.get('vehicle_id', type=int) or None
#     booking_date_str = request.form.get('booking_date', '')
#     booking_time_str = request.form.get('booking_time', '')
#     notes = request.form.get('notes', '')

#     try:
#         b_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
#         b_time = datetime.strptime(booking_time_str, '%H:%M').time()
#     except ValueError:
#         flash('Invalid date or time.', 'danger')
#         return redirect(url_for('user.garage_detail', garage_id=garage_id))

#     if b_date < date.today():
#         flash('Cannot book a past date.', 'danger')
#         return redirect(url_for('user.garage_detail', garage_id=garage_id))

@user_bp.route('/book', methods=['POST'])
@login_required
def book_service():
    garage_id = request.form.get('garage_id', type=int)
    service_id = request.form.get('service_id', type=int)

    # ✅ ADD THIS CHECK
    if not service_id:
        flash('Please select a service first.', 'danger')
        return redirect(url_for('user.garage_detail', garage_id=garage_id))

    vehicle_id = request.form.get('vehicle_id', type=int) or None
    booking_date_str = request.form.get('booking_date', '')
    booking_time_str = request.form.get('booking_time', '')
    notes = request.form.get('notes', '')

    try:
        b_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        b_time = datetime.strptime(booking_time_str, '%H:%M').time()
    except ValueError:
        flash('Invalid date or time.', 'danger')
        return redirect(url_for('user.garage_detail', garage_id=garage_id))
    
    service = Service.query.get_or_404(service_id)
    booking = Booking(
        user_id=current_user.id,
        garage_id=garage_id,
        service_id=service_id,
        vehicle_id=vehicle_id,
        booking_date=b_date,
        booking_time=b_time,
        notes=notes,
        total_amount=service.price
    )
    db.session.add(booking)
    db.session.commit()
    flash('Booking submitted! Awaiting garage confirmation.', 'success')
    return redirect(url_for('user.my_bookings'))


@user_bp.route('/bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('user/bookings.html', bookings=bookings)


@user_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.my_bookings'))
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        db.session.commit()
        flash('Booking cancelled.', 'info')
    else:
        flash('Cannot cancel this booking.', 'warning')
    return redirect(url_for('user.my_bookings'))


# --- Vehicles ---
# @user_bp.route('/vehicles')
# @login_required
# def vehicles():
#     vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
#     return render_template('user/vehicles.html', vehicles=vehicles)
from datetime import date   # ✅ add this at top

# --- Vehicles ---
@user_bp.route('/vehicles')
@login_required
def vehicles():
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    
    today = date.today()   # ✅ add this

    return render_template(
        'user/vehicles.html',
        vehicles=vehicles,
        today=today        # ✅ pass this
    )

@user_bp.route('/vehicle/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        v = Vehicle(
            user_id=current_user.id,
            reg_number=request.form['reg_number'].upper(),
            make=request.form['make'],
            model=request.form['model'],
            year=request.form.get('year', type=int),
            color=request.form.get('color', ''),
            insurance_number=request.form.get('insurance_number', ''),
            insurance_expiry=datetime.strptime(request.form['insurance_expiry'], '%Y-%m-%d').date()
                if request.form.get('insurance_expiry') else None
        )
        db.session.add(v)
        db.session.commit()
        flash('Vehicle added!', 'success')
        return redirect(url_for('user.vehicles'))
    return render_template('user/add_vehicle.html')


@user_bp.route('/vehicle/delete/<int:vid>', methods=['POST'])
@login_required
def delete_vehicle(vid):
    v = Vehicle.query.get_or_404(vid)
    if v.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.vehicles'))
    db.session.delete(v)
    db.session.commit()
    flash('Vehicle removed.', 'info')
    return redirect(url_for('user.vehicles'))


# --- Documents ---
@user_bp.route('/documents')
@login_required
def documents():
    docs = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('user/documents.html', documents=docs)


@user_bp.route('/document/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    if request.method == 'POST':
        file = request.files.get('document')
        doc_type = request.form.get('doc_type', 'Other')
        expiry = request.form.get('expiry_date', '')
        notes = request.form.get('notes', '')

        if not file or not allowed_file(file.filename):
            flash('Invalid file type. Allowed: png, jpg, jpeg, gif, pdf', 'danger')
            return render_template('user/upload_document.html')

        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)

        doc = Document(
            user_id=current_user.id,
            doc_type=doc_type,
            filename=unique_name,
            original_name=file.filename,
            file_size=os.path.getsize(upload_path),
            expiry_date=datetime.strptime(expiry, '%Y-%m-%d').date() if expiry else None,
            notes=notes
        )
        db.session.add(doc)
        db.session.commit()
        flash('Document uploaded!', 'success')
        return redirect(url_for('user.documents'))

    return render_template('user/upload_document.html')


@user_bp.route('/document/delete/<int:did>', methods=['POST'])
@login_required
def delete_document(did):
    doc = Document.query.get_or_404(did)
    if doc.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.documents'))
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted.', 'info')
    return redirect(url_for('user.documents'))


# --- SOS ---
@user_bp.route('/sos', methods=['GET', 'POST'])
@login_required
def sos():
    if request.method == 'POST':
        lat = request.form.get('latitude', type=float) or 19.0760
        lon = request.form.get('longitude', type=float) or 72.8777
        message = request.form.get('message', 'Emergency! Need immediate assistance.')
        address = request.form.get('address', '')

        # Find nearest active garage
        garages = Garage.query.filter_by(is_active=True).all()
        nearest = None
        min_dist = float('inf')
        for g in garages:
            d = haversine(lat, lon, g.latitude, g.longitude)
            if d < min_dist:
                min_dist = d
                nearest = g

        alert = SOSAlert(
            user_id=current_user.id,
            garage_id=nearest.id if nearest else None,
            latitude=lat,
            longitude=lon,
            address=address,
            message=message
        )
        db.session.add(alert)
        db.session.commit()
        flash(f'🚨 SOS Alert sent! Nearest garage "{nearest.name if nearest else "N/A"}" has been notified.', 'danger')
        return redirect(url_for('user.dashboard'))

    return render_template('user/sos.html')


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.emergency_contact = request.form.get('emergency_contact', '')
        lat = request.form.get('latitude', type=float)
        lon = request.form.get('longitude', type=float)
        if lat: current_user.latitude = lat
        if lon: current_user.longitude = lon
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html')
