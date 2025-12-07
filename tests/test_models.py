"""
Tests for Database Models
"""
import pytest
from datetime import datetime, date, time
from models import db, User, Train, Route, Schedule, Ticket, Seat, Payment


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, app):
        """Test creating a user"""
        with app.app_context():
            user = User(
                username='modeltest',
                email='modeltest@test.com',
                full_name='Model Test User',
                phone='1234567890',
                role='user'
            )
            user.set_password('testpassword')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'modeltest'
            assert user.role == 'user'
    
    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(
                username='hashtest',
                email='hashtest@test.com',
                full_name='Hash Test'
            )
            user.set_password('mysecretpassword')
            
            # Password should be hashed
            assert user.password_hash != 'mysecretpassword'
            
            # Verification should work
            assert user.check_password('mysecretpassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_to_dict(self, app):
        """Test user serialization"""
        with app.app_context():
            user = User(
                username='dicttest',
                email='dicttest@test.com',
                full_name='Dict Test',
                phone='9999999999',
                role='admin'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            assert 'id' in user_dict
            assert user_dict['username'] == 'dicttest'
            assert user_dict['email'] == 'dicttest@test.com'
            assert 'password' not in user_dict
            assert 'password_hash' not in user_dict


class TestTrainModel:
    """Test Train model"""
    
    def test_create_train(self, app):
        """Test creating a train"""
        with app.app_context():
            train = Train(
                train_number='TEST001',
                train_name='Test Express',
                train_type='express',
                total_seats=100,
                status='active'
            )
            
            db.session.add(train)
            db.session.commit()
            
            assert train.id is not None
            assert train.train_number == 'TEST001'
    
    def test_train_to_dict(self, app):
        """Test train serialization"""
        with app.app_context():
            train = Train(
                train_number='DICT001',
                train_name='Dict Train',
                train_type='superfast',
                total_seats=200,
                status='active'
            )
            db.session.add(train)
            db.session.commit()
            
            train_dict = train.to_dict()
            
            assert train_dict['train_number'] == 'DICT001'
            assert train_dict['train_type'] == 'superfast'
            assert train_dict['total_seats'] == 200


class TestRouteModel:
    """Test Route model"""
    
    def test_create_route(self, app):
        """Test creating a route"""
        with app.app_context():
            route = Route(
                route_name='Test Route',
                source_station='Source City',
                destination_station='Dest City',
                distance_km=250.5,
                duration_hours=4.5,
                status='active'
            )
            
            db.session.add(route)
            db.session.commit()
            
            assert route.id is not None
            assert route.distance_km == 250.5
    
    def test_route_to_dict(self, app):
        """Test route serialization"""
        with app.app_context():
            route = Route(
                route_name='Dict Route',
                source_station='A',
                destination_station='B',
                distance_km=100.0,
                duration_hours=2.0,
                status='active'
            )
            db.session.add(route)
            db.session.commit()
            
            route_dict = route.to_dict()
            
            assert route_dict['route_name'] == 'Dict Route'
            assert route_dict['distance_km'] == 100.0
            assert route_dict['duration_hours'] == 2.0


class TestScheduleModel:
    """Test Schedule model"""
    
    def test_create_schedule(self, app):
        """Test creating a schedule"""
        with app.app_context():
            # Create dependencies
            train = Train(
                train_number='SCH001',
                train_name='Schedule Train',
                train_type='local',
                total_seats=50,
                status='active'
            )
            route = Route(
                route_name='Schedule Route',
                source_station='X',
                destination_station='Y',
                distance_km=100,
                duration_hours=2,
                status='active'
            )
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(9, 0, 0),
                arrival_time=time(11, 0, 0),
                frequency='daily',
                base_fare=50.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            assert schedule.id is not None
            assert schedule.train_id == train.id
            assert schedule.route_id == route.id
    
    def test_schedule_relationships(self, app):
        """Test schedule relationships with train and route"""
        with app.app_context():
            train = Train(
                train_number='REL001',
                train_name='Relation Train',
                train_type='express',
                total_seats=100,
                status='active'
            )
            route = Route(
                route_name='Relation Route',
                source_station='P',
                destination_station='Q',
                distance_km=200,
                duration_hours=3,
                status='active'
            )
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(10, 0, 0),
                arrival_time=time(13, 0, 0),
                frequency='weekly',
                base_fare=75.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            # Test relationships
            assert schedule.train.train_name == 'Relation Train'
            assert schedule.route.route_name == 'Relation Route'


class TestTicketModel:
    """Test Ticket model"""
    
    def test_create_ticket(self, app):
        """Test creating a ticket"""
        with app.app_context():
            # Create dependencies
            user = User(
                username='ticketuser',
                email='ticketuser@test.com',
                full_name='Ticket User'
            )
            user.set_password('password')
            
            train = Train(
                train_number='TKT001',
                train_name='Ticket Train',
                train_type='express',
                total_seats=100,
                status='active'
            )
            route = Route(
                route_name='Ticket Route',
                source_station='T',
                destination_station='U',
                distance_km=150,
                duration_hours=2.5,
                status='active'
            )
            db.session.add(user)
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(14, 0, 0),
                arrival_time=time(16, 30, 0),
                frequency='daily',
                base_fare=100.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            ticket = Ticket(
                user_id=user.id,
                schedule_id=schedule.id,
                booking_date=date.today(),
                journey_date=date.today(),
                passenger_name='Test Passenger',
                passenger_age=30,
                passenger_gender='male',
                seat_number='A1',
                fare=100.00,
                status='confirmed',
                pnr_number='TEST123456'
            )
            db.session.add(ticket)
            db.session.commit()
            
            assert ticket.id is not None
            assert ticket.pnr_number == 'TEST123456'


class TestSeatModel:
    """Test Seat model"""
    
    def test_create_seat(self, app):
        """Test creating a seat"""
        with app.app_context():
            train = Train(
                train_number='SEAT001',
                train_name='Seat Train',
                train_type='local',
                total_seats=50,
                status='active'
            )
            route = Route(
                route_name='Seat Route',
                source_station='S',
                destination_station='E',
                distance_km=100,
                duration_hours=2,
                status='active'
            )
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(8, 0, 0),
                arrival_time=time(10, 0, 0),
                frequency='daily',
                base_fare=50.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            seat = Seat(
                schedule_id=schedule.id,
                journey_date=date.today(),
                seat_number='A1',
                seat_type='AC',
                is_available=True
            )
            db.session.add(seat)
            db.session.commit()
            
            assert seat.id is not None
            assert seat.is_available is True
    
    def test_seat_unique_constraint(self, app):
        """Test seat unique constraint"""
        with app.app_context():
            train = Train(
                train_number='UNQ001',
                train_name='Unique Train',
                train_type='express',
                total_seats=100,
                status='active'
            )
            route = Route(
                route_name='Unique Route',
                source_station='U',
                destination_station='N',
                distance_km=150,
                duration_hours=2.5,
                status='active'
            )
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(12, 0, 0),
                arrival_time=time(14, 30, 0),
                frequency='daily',
                base_fare=75.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            journey = date.today()
            
            seat1 = Seat(
                schedule_id=schedule.id,
                journey_date=journey,
                seat_number='B1',
                seat_type='sleeper',
                is_available=True
            )
            db.session.add(seat1)
            db.session.commit()
            
            # Try to create duplicate seat
            seat2 = Seat(
                schedule_id=schedule.id,
                journey_date=journey,
                seat_number='B1',  # Same seat number
                seat_type='sleeper',
                is_available=True
            )
            db.session.add(seat2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()


class TestPaymentModel:
    """Test Payment model"""
    
    def test_create_payment(self, app):
        """Test creating a payment"""
        with app.app_context():
            # Create all dependencies
            user = User(
                username='payuser',
                email='payuser@test.com',
                full_name='Pay User'
            )
            user.set_password('password')
            
            train = Train(
                train_number='PAY001',
                train_name='Pay Train',
                train_type='express',
                total_seats=100,
                status='active'
            )
            route = Route(
                route_name='Pay Route',
                source_station='P',
                destination_station='A',
                distance_km=200,
                duration_hours=3,
                status='active'
            )
            db.session.add(user)
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(16, 0, 0),
                arrival_time=time(19, 0, 0),
                frequency='daily',
                base_fare=150.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            ticket = Ticket(
                user_id=user.id,
                schedule_id=schedule.id,
                booking_date=date.today(),
                journey_date=date.today(),
                passenger_name='Pay Passenger',
                passenger_age=25,
                passenger_gender='female',
                fare=150.00,
                status='confirmed',
                pnr_number='PAY1234567'
            )
            db.session.add(ticket)
            db.session.commit()
            
            payment = Payment(
                ticket_id=ticket.id,
                user_id=user.id,
                amount=150.00,
                payment_method='credit_card',
                payment_status='completed',
                transaction_id='TXN123456789'
            )
            db.session.add(payment)
            db.session.commit()
            
            assert payment.id is not None
            assert payment.amount == 150.00
            assert payment.payment_status == 'completed'
    
    def test_payment_to_dict(self, app):
        """Test payment serialization"""
        with app.app_context():
            user = User(
                username='paydict',
                email='paydict@test.com',
                full_name='Pay Dict'
            )
            user.set_password('password')
            
            train = Train(
                train_number='PDICT01',
                train_name='Dict Train',
                train_type='local',
                total_seats=50,
                status='active'
            )
            route = Route(
                route_name='Dict Route',
                source_station='D',
                destination_station='I',
                distance_km=100,
                duration_hours=2,
                status='active'
            )
            db.session.add(user)
            db.session.add(train)
            db.session.add(route)
            db.session.commit()
            
            schedule = Schedule(
                train_id=train.id,
                route_id=route.id,
                departure_time=time(7, 0, 0),
                arrival_time=time(9, 0, 0),
                frequency='daily',
                base_fare=50.00,
                status='active'
            )
            db.session.add(schedule)
            db.session.commit()
            
            ticket = Ticket(
                user_id=user.id,
                schedule_id=schedule.id,
                booking_date=date.today(),
                journey_date=date.today(),
                passenger_name='Dict Passenger',
                passenger_age=28,
                passenger_gender='male',
                fare=50.00,
                status='confirmed',
                pnr_number='DICT123456'
            )
            db.session.add(ticket)
            db.session.commit()
            
            payment = Payment(
                ticket_id=ticket.id,
                user_id=user.id,
                amount=50.00,
                payment_method='upi',
                payment_status='completed',
                transaction_id='UPITXN12345'
            )
            db.session.add(payment)
            db.session.commit()
            
            payment_dict = payment.to_dict()
            
            assert payment_dict['amount'] == 50.00
            assert payment_dict['payment_method'] == 'upi'
            assert payment_dict['transaction_id'] == 'UPITXN12345'
