from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User, ParkingLot, ParkingSpot, Reservation
from forms import LoginForm, RegisterForm, ParkingLotForm
from utils import (create_parking_spots, update_parking_spots, book_parking_spot, 
                  release_parking_spot, get_dashboard_stats, get_user_dashboard_stats)
from datetime import datetime

@app.route('/')
def index():
    """Home page"""
    lots = ParkingLot.query.all()
    return render_template('index.html', lots=lots)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both admin and users"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    stats = get_dashboard_stats()
    lots = ParkingLot.query.all()
    
    return render_template('admin_dashboard.html', stats=stats, lots=lots)

@app.route('/admin/create-lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    """Create new parking lot"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    form = ParkingLotForm()
    if form.validate_on_submit():
        lot = ParkingLot(
            prime_location_name=form.prime_location_name.data,
            address=form.address.data,
            pin_code=form.pin_code.data,
            price_per_hour=form.price_per_hour.data,
            maximum_number_of_spots=form.maximum_number_of_spots.data
        )
        db.session.add(lot)
        db.session.commit()
        
        # Create parking spots
        create_parking_spots(lot.id, lot.maximum_number_of_spots)
        
        flash('Parking lot created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html', form=form)

@app.route('/admin/edit-lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    """Edit parking lot"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    form = ParkingLotForm(obj=lot)
    
    if form.validate_on_submit():
        old_spots_count = lot.maximum_number_of_spots
        
        lot.prime_location_name = form.prime_location_name.data
        lot.address = form.address.data
        lot.pin_code = form.pin_code.data
        lot.price_per_hour = form.price_per_hour.data
        lot.maximum_number_of_spots = form.maximum_number_of_spots.data
        
        # Update parking spots if number changed
        if old_spots_count != lot.maximum_number_of_spots:
            update_parking_spots(lot.id, lot.maximum_number_of_spots)
        
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_lot.html', form=form, lot=lot)

@app.route('/admin/delete-lot/<int:lot_id>')
@login_required
def delete_lot(lot_id):
    """Delete parking lot"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if all spots are available
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occupied_spots > 0:
        flash('Cannot delete parking lot. Some spots are currently occupied.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/view-users')
@login_required
def view_users():
    """View all registered users"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.filter_by(is_admin=False).all()
    return render_template('view_users.html', users=users)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    stats = get_user_dashboard_stats(current_user.id)
    active_reservations = Reservation.query.filter_by(
        user_id=current_user.id,
        leaving_timestamp=None
    ).all()
    
    recent_reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).order_by(Reservation.created_at.desc()).limit(5).all()
    
    return render_template('user_dashboard.html', 
                         stats=stats, 
                         active_reservations=active_reservations,
                         recent_reservations=recent_reservations)

@app.route('/user/book-parking', methods=['GET', 'POST'])
@login_required
def book_parking():
    """Book parking spot"""
    if current_user.is_admin:
        flash('Admin cannot book parking spots.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Check if user has active reservation
    active_reservation = Reservation.query.filter_by(
        user_id=current_user.id,
        leaving_timestamp=None
    ).first()
    
    if active_reservation:
        flash('You already have an active parking reservation.', 'error')
        return redirect(url_for('user_dashboard'))
    
    lots_with_availability = []
    lots = ParkingLot.query.all()
    for lot in lots:
        if lot.available_spots_count > 0:
            lots_with_availability.append(lot)
    
    if request.method == 'POST':
        lot_id = request.form.get('lot_id')
        if not lot_id:
            flash('Please select a parking lot.', 'error')
            return render_template('book_parking.html', lots=lots_with_availability)
        
        reservation, message = book_parking_spot(current_user.id, int(lot_id))
        if reservation:
            flash(f'{message} Spot #{reservation.spot.spot_number} assigned.', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('book_parking.html', lots=lots_with_availability)

@app.route('/user/release-parking/<int:reservation_id>')
@login_required
def release_parking(reservation_id):
    """Release parking spot"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Check if user owns this reservation
    if reservation.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('user_dashboard'))
    
    success, message = release_parking_spot(reservation_id)
    if success:
        flash(f'{message} Total cost: ₹{reservation.total_cost}', 'success')
    else:
        flash(message, 'error')
    
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/api/parking-stats')
@login_required
def parking_stats_api():
    """API endpoint for parking statistics (for charts)"""
    try:
        if current_user.is_admin:
            stats = get_dashboard_stats()
            lots_data = []
            for lot in ParkingLot.query.all():
                lots_data.append({
                    'name': lot.prime_location_name,
                    'available': lot.available_spots_count,
                    'occupied': lot.occupied_spots_count,
                    'total': lot.maximum_number_of_spots
                })
            
            return jsonify({
                'overview': stats,
                'lots': lots_data,
                'success': True
            })
        else:
            stats = get_user_dashboard_stats(current_user.id)
            reservations = Reservation.query.filter_by(user_id=current_user.id).all()
            monthly_data = {}
            
            for reservation in reservations:
                if reservation.parking_timestamp:
                    month = reservation.parking_timestamp.strftime('%Y-%m')
                    if month not in monthly_data:
                        monthly_data[month] = 0
                    if reservation.total_cost:
                        monthly_data[month] += reservation.total_cost
            
            return jsonify({
                'overview': stats,
                'monthly_spending': monthly_data,
                'success': True
            })
    except Exception as e:
        app.logger.error(f"Error in parking_stats_api: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
