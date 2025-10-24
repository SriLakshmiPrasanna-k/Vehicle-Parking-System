from database import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with reservations
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False, default=10.0)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with parking spots
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all, delete-orphan')
    
    @property
    def available_spots_count(self):
        return ParkingSpot.query.filter_by(lot_id=self.id, status='A').count()
    
    @property
    def occupied_spots_count(self):
        return ParkingSpot.query.filter_by(lot_id=self.id, status='O').count()
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)  # A=Available, O=Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with reservations
    reservations = db.relationship('Reservation', backref='spot', lazy=True)
    
    @property
    def current_reservation(self):
        try:
            return Reservation.query.filter_by(
                spot_id=self.id,
                leaving_timestamp=None
            ).first()
        except Exception:
            return None
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} in Lot {self.lot_id}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost_per_hour = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def duration_hours(self):
        if self.leaving_timestamp:
            duration = self.leaving_timestamp - self.parking_timestamp
            return round(duration.total_seconds() / 3600, 2)
        else:
            duration = datetime.utcnow() - self.parking_timestamp
            return round(duration.total_seconds() / 3600, 2)
    
    @property
    def calculated_cost(self):
        return round(self.duration_hours * self.parking_cost_per_hour, 2)
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id} - Spot {self.spot_id}>'
