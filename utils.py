from datetime import datetime
from models import ParkingSpot, ParkingLot, Reservation, User
from app import db

def create_parking_spots(lot_id, number_of_spots):
    """Create parking spots for a parking lot"""
    for i in range(1, number_of_spots + 1):
        spot = ParkingSpot(
            lot_id=lot_id,
            spot_number=i,
            status='A'
        )
        db.session.add(spot)
    db.session.commit()

def update_parking_spots(lot_id, new_number_of_spots):
    """Update the number of parking spots for a lot"""
    current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
    
    if new_number_of_spots > current_spots:
        # Add new spots
        for i in range(current_spots + 1, new_number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=lot_id,
                spot_number=i,
                status='A'
            )
            db.session.add(spot)
    elif new_number_of_spots < current_spots:
        # Remove spots (only if they are available)
        spots_to_remove = ParkingSpot.query.filter_by(
            lot_id=lot_id,
            status='A'
        ).filter(
            ParkingSpot.spot_number > new_number_of_spots
        ).all()
        
        for spot in spots_to_remove:
            db.session.delete(spot)
    
    db.session.commit()

def get_available_spot(lot_id):
    """Get the first available spot in a parking lot"""
    return ParkingSpot.query.filter_by(
        lot_id=lot_id,
        status='A'
    ).order_by(ParkingSpot.spot_number).first()

def book_parking_spot(user_id, lot_id):
    """Book a parking spot for a user"""
    # Get first available spot
    spot = get_available_spot(lot_id)
    if not spot:
        return None, "No available spots in this parking lot"
    
    # Get lot details for pricing
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return None, "Parking lot not found"
    
    # Create reservation
    reservation = Reservation(
        spot_id=spot.id,
        user_id=user_id,
        parking_cost_per_hour=lot.price_per_hour
    )
    
    # Update spot status
    spot.status = 'O'
    
    db.session.add(reservation)
    db.session.commit()
    
    return reservation, "Parking spot booked successfully"

def release_parking_spot(reservation_id):
    """Release a parking spot"""
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return False, "Reservation not found"
    
    if reservation.leaving_timestamp:
        return False, "Parking spot already released"
    
    # Update reservation
    reservation.leaving_timestamp = datetime.utcnow()
    reservation.total_cost = reservation.calculated_cost
    
    # Update spot status
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'
    
    db.session.commit()
    
    return True, "Parking spot released successfully"

def get_dashboard_stats():
    """Get statistics for admin dashboard"""
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    total_users = User.query.filter_by(is_admin=False).count()
    active_reservations = Reservation.query.filter_by(leaving_timestamp=None).count()
    
    return {
        'total_lots': total_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots,
        'total_users': total_users,
        'active_reservations': active_reservations
    }

def get_user_dashboard_stats(user_id):
    """Get statistics for user dashboard"""
    total_reservations = Reservation.query.filter_by(user_id=user_id).count()
    active_reservations = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).count()
    completed_reservations = Reservation.query.filter_by(user_id=user_id).filter(Reservation.leaving_timestamp.isnot(None)).count()
    
    total_spent = db.session.query(db.func.sum(Reservation.total_cost)).filter_by(user_id=user_id).scalar() or 0
    
    return {
        'total_reservations': total_reservations,
        'active_reservations': active_reservations,
        'completed_reservations': completed_reservations,
        'total_spent': round(total_spent, 2)
    }
