"""
Pytest configuration and fixtures for Train Booking System tests
"""
import pytest
import sys
import os
from datetime import date, time, timedelta

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables BEFORE importing app
# This ensures the app uses these settings when create_app() is called
os.environ.setdefault('MYSQL_HOST', '127.0.0.1')
os.environ.setdefault('MYSQL_PORT', '3306')
os.environ.setdefault('MYSQL_USER', 'trainuser')
os.environ.setdefault('MYSQL_PASSWORD', 'trainpass')
os.environ.setdefault('MYSQL_DATABASE', 'train_booking_db')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from app import create_app
from models import db, User, Train, Route, Schedule, Ticket, Seat, Payment
from config import TestingConfig


class TestConfig(TestingConfig):
    """Test configuration with SQLite in-memory database"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture
def app():
    """Create application for testing"""
    # Create app with test config
    _app = create_app(TestConfig)
    
    with _app.app_context():
        db.create_all()
        yield _app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            email='admin@test.com',
            full_name='Admin User',
            phone='1234567890',
            role='admin'
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        
        # Create regular user
        user = User(
            username='testuser',
            email='testuser@test.com',
            full_name='Test User',
            phone='0987654321',
            role='user'
        )
        user.set_password('userpass123')
        db.session.add(user)
        
        # Create train
        train = Train(
            train_number='EXP001',
            train_name='Express One',
            train_type='express',
            total_seats=100,
            status='active'
        )
        db.session.add(train)
        
        # Create route
        route = Route(
            route_name='City A to City B',
            source_station='City A',
            destination_station='City B',
            distance_km=500.0,
            duration_hours=6.5,
            status='active'
        )
        db.session.add(route)
        
        db.session.commit()
        
        # Create schedule (needs train and route IDs)
        schedule = Schedule(
            train_id=train.id,
            route_id=route.id,
            departure_time=time(8, 0, 0),
            arrival_time=time(14, 30, 0),
            frequency='daily',
            base_fare=150.00,
            status='active'
        )
        db.session.add(schedule)
        db.session.commit()
        
        # Create seats for future date
        future_date = date.today() + timedelta(days=7)
        for i in range(1, 6):
            seat = Seat(
                schedule_id=schedule.id,
                journey_date=future_date,
                seat_number=f'A{i}',
                seat_type='AC',
                is_available=True
            )
            db.session.add(seat)
        
        db.session.commit()
        
        yield {
            'admin': admin,
            'user': user,
            'train': train,
            'route': route,
            'schedule': schedule,
            'future_date': future_date
        }


def login_user(client, username, password):
    """Helper function to login a user"""
    return client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })


def login_admin(client):
    """Helper function to login as admin"""
    return login_user(client, 'admin', 'adminpass123')


def login_regular_user(client):
    """Helper function to login as regular user"""
    return login_user(client, 'testuser', 'userpass123')
