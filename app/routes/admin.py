from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Garage, Service, Booking, SOSAlert, User
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_admin_garage():
    return Garage.query.filter_by(admin_id=current_user.id).first()


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    garage = get_admin_garage()
    if not garage:
        flash('Please set up your garage profile first.', 'warning')
        return redirect(url_for('admin.garage_profile'))

    total_bookings = Booking.query.filter_by(garage_id=garage.id).count()
    pending = Booking.query.filter_by(garage_id=garage.id, status='pending').count()
    confirmed = Booking.query.filter_by(garage_id=garage.id, status='confirmed').count()
    completed = Booking.query.filter_by(garage_id=garage.id, status='completed').count()
    sos_alerts = SOSAlert.query.filter_by(garage_id=garage.id, status='active').count()
    recent_bookings = Booking.query.filter_by(garage_id=garage.id).order_by(Booking.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', garage=garage, total_bookings=total_bookings,
                           pending=pending, confirmed=confirmed, completed=completed,
                           sos_count=sos_alerts, recent_bookings=recent_bookings)


@admin_bp.route('/garage/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def garage_profile():
    garage = get_admin_garage()
    if request.method == 'POST':
        if garage:
            garage.name = request.form['name']
            garage.address = request.form['address']
            garage.city = request.form['city']
            garage.phone = request.form.get('phone', '')
            garage.email = request.form.get('email', '')
            garage.description = request.form.get('description', '')
            garage.open_time = request.form.get('open_time', '09:00')
            garage.close_time = request.form.get('close_time', '20:00')
            lat = request.form.get('latitude', type=float)
            lon = request.form.get('longitude', type=float)
            if lat: garage.latitude = lat
            if lon: garage.longitude = lon
        else:
            garage = Garage(
                admin_id=current_user.id,
                name=request.form['name'],
                address=request.form['address'],
                city=request.form['city'],
                phone=request.form.get('phone', ''),
                email=request.form.get('email', ''),
                description=request.form.get('description', ''),
                latitude=request.form.get('latitude', type=float) or 19.0760,
                longitude=request.form.get('longitude', type=float) or 72.8777,
            )
            db.session.add(garage)
        db.session.commit()
        flash('Garage profile updated!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/garage_profile.html', garage=garage)


@admin_bp.route('/services')
@login_required
@admin_required
def services():
    garage = get_admin_garage()
    if not garage:
        flash('Set up garage first.', 'warning')
        return redirect(url_for('admin.garage_profile'))
    services = Service.query.filter_by(garage_id=garage.id).all()
    return render_template('admin/services.html', services=services, garage=garage)


@admin_bp.route('/service/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    garage = get_admin_garage()
    if not garage:
        return redirect(url_for('admin.garage_profile'))
    if request.method == 'POST':
        s = Service(
            garage_id=garage.id,
            name=request.form['name'],
            description=request.form.get('description', ''),
            price=float(request.form['price']),
            duration_minutes=int(request.form.get('duration', 60))
        )
        db.session.add(s)
        db.session.commit()
        flash('Service added!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/add_service.html')


@admin_bp.route('/service/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(sid):
    service = Service.query.get_or_404(sid)
    garage = get_admin_garage()
    if service.garage_id != garage.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('admin.services'))
    if request.method == 'POST':
        service.name = request.form['name']
        service.description = request.form.get('description', '')
        service.price = float(request.form['price'])
        service.duration_minutes = int(request.form.get('duration', 60))
        service.is_available = 'is_available' in request.form
        db.session.commit()
        flash('Service updated!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/edit_service.html', service=service)


@admin_bp.route('/service/delete/<int:sid>', methods=['POST'])
@login_required
@admin_required
def delete_service(sid):
    service = Service.query.get_or_404(sid)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted.', 'info')
    return redirect(url_for('admin.services'))


@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    garage = get_admin_garage()
    if not garage:
        return redirect(url_for('admin.garage_profile'))
    status_filter = request.args.get('status', '')
    query = Booking.query.filter_by(garage_id=garage.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings, status_filter=status_filter)


@admin_bp.route('/booking/update/<int:bid>/<status>', methods=['POST'])
@login_required
@admin_required
def update_booking(bid, status):
    booking = Booking.query.get_or_404(bid)
    garage = get_admin_garage()
    if booking.garage_id != garage.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('admin.bookings'))
    valid_statuses = ['confirmed', 'rejected', 'completed']
    if status in valid_statuses:
        booking.status = status
        db.session.commit()
        flash(f'Booking {status}.', 'success')
    return redirect(url_for('admin.bookings'))


@admin_bp.route('/sos-alerts')
@login_required
@admin_required
def sos_alerts():
    garage = get_admin_garage()
    if not garage:
        return redirect(url_for('admin.garage_profile'))
    alerts = SOSAlert.query.filter_by(garage_id=garage.id).order_by(SOSAlert.created_at.desc()).all()
    return render_template('admin/sos_alerts.html', alerts=alerts)


@admin_bp.route('/sos/resolve/<int:aid>', methods=['POST'])
@login_required
@admin_required
def resolve_sos(aid):
    from datetime import datetime
    alert = SOSAlert.query.get_or_404(aid)
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    flash('SOS alert resolved.', 'success')
    return redirect(url_for('admin.sos_alerts'))


@admin_bp.route('/customers')
@login_required
@admin_required
def customers():
    garage = get_admin_garage()
    if not garage:
        return redirect(url_for('admin.garage_profile'))
    user_ids = db.session.query(Booking.user_id).filter_by(garage_id=garage.id).distinct().all()
    user_ids = [uid[0] for uid in user_ids]
    customers = User.query.filter(User.id.in_(user_ids)).all()
    return render_template('admin/customers.html', customers=customers)
