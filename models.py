"""
SQLAlchemy Models for Train Booking System
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('user', 'admin', name='user_roles'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Train(db.Model):
    """Train model for train information"""
    __tablename__ = 'trains'
    
    id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    train_name = db.Column(db.String(100), nullable=False)
    train_type = db.Column(db.Enum('express', 'local', 'superfast', 'premium', name='train_types'), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'maintenance', name='train_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('Schedule', backref='train', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'train_number': self.train_number,
            'train_name': self.train_name,
            'train_type': self.train_type,
            'total_seats': self.total_seats,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Route(db.Model):
    """Route model for train routes"""
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    source_station = db.Column(db.String(100), nullable=False, index=True)
    destination_station = db.Column(db.String(100), nullable=False, index=True)
    distance_km = db.Column(db.Numeric(10, 2), nullable=False)
    duration_hours = db.Column(db.Numeric(5, 2), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', name='route_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('Schedule', backref='route', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'route_name': self.route_name,
            'source_station': self.source_station,
            'destination_station': self.destination_station,
            'distance_km': float(self.distance_km) if self.distance_km else 0,
            'duration_hours': float(self.duration_hours) if self.duration_hours else 0,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Schedule(db.Model):
    """Schedule model linking trains to routes"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.id', ondelete='CASCADE'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    frequency = db.Column(db.Enum('daily', 'weekly', 'weekend', name='frequency_types'), nullable=False)
    base_fare = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('active', 'cancelled', 'delayed', name='schedule_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='schedule', lazy=True, cascade='all, delete-orphan')
    seats = db.relationship('Seat', backref='schedule', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'train_id': self.train_id,
            'route_id': self.route_id,
            'train_name': self.train.train_name if self.train else None,
            'train_number': self.train.train_number if self.train else None,
            'source_station': self.route.source_station if self.route else None,
            'destination_station': self.route.destination_station if self.route else None,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'frequency': self.frequency,
            'base_fare': float(self.base_fare) if self.base_fare else 0,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Ticket(db.Model):
    """Ticket model for bookings"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    journey_date = db.Column(db.Date, nullable=False, index=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_age = db.Column(db.Integer, nullable=False)
    passenger_gender = db.Column(db.Enum('male', 'female', 'other', name='gender_types'), nullable=False)
    seat_number = db.Column(db.String(10))
    fare = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('confirmed', 'cancelled', 'pending', 'waitlisted', name='ticket_status'), default='pending')
    pnr_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    seat = db.relationship('Seat', backref='ticket', lazy=True, uselist=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'schedule_id': self.schedule_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'journey_date': self.journey_date.isoformat() if self.journey_date else None,
            'passenger_name': self.passenger_name,
            'passenger_age': self.passenger_age,
            'passenger_gender': self.passenger_gender,
            'seat_number': self.seat_number,
            'fare': float(self.fare) if self.fare else 0,
            'status': self.status,
            'pnr_number': self.pnr_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Seat(db.Model):
    """Seat model for seat management"""
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False, index=True)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_type = db.Column(db.Enum('sleeper', 'AC', 'general', 'first_class', name='seat_types'), nullable=False)
    is_available = db.Column(db.Boolean, default=True, index=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('schedule_id', 'journey_date', 'seat_number', name='unique_seat_schedule_date'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'journey_date': self.journey_date.isoformat() if self.journey_date else None,
            'seat_number': self.seat_number,
            'seat_type': self.seat_type,
            'is_available': self.is_available,
            'ticket_id': self.ticket_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Payment(db.Model):
    """Payment model for transaction records"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('credit_card', 'debit_card', 'upi', 'netbanking', 'wallet', name='payment_methods'), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'), default='pending')
    transaction_id = db.Column(db.String(100), unique=True, index=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'amount': float(self.amount) if self.amount else 0,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
