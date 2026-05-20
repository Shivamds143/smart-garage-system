from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User, Garage

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard') if current_user.role == 'user' else url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            flash(f'Welcome back, {user.name}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')
        garage_name = request.form.get('garage_name', '').strip()
        garage_address = request.form.get('garage_address', '').strip()
        garage_city = request.form.get('garage_city', '').strip()

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')

        user = User(name=name, email=email, phone=phone, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'admin' and garage_name:
            garage = Garage(
                admin_id=user.id,
                name=garage_name,
                address=garage_address or 'Address not set',
                city=garage_city or 'City not set',
                phone=phone
            )
            db.session.add(garage)

        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
