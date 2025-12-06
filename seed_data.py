"""
Seed data script to populate the database with initial data
Run this after the application starts for the first time
"""
from app import create_app
from models import db, User, Train, Route, Schedule, Seat
from datetime import datetime, date, timedelta

def seed_database():
    """Populate database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data (optional - comment out in production)
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@trainbooking.com',
            full_name='System Administrator',
            phone='1234567890',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular users
        print("Creating sample users...")
        user1 = User(
            username='john_doe',
            email='john@example.com',
            full_name='John Doe',
            phone='9876543210',
            role='user'
        )
        user1.set_password('password123')
        db.session.add(user1)
        
        user2 = User(
            username='jane_smith',
            email='jane@example.com',
            full_name='Jane Smith',
            phone='9876543211',
            role='user'
        )
        user2.set_password('password123')
        db.session.add(user2)
        
        # Create trains
        print("Creating trains...")
        trains = [
            Train(
                train_number='12345',
                train_name='Rajdhani Express',
                train_type='superfast',
                total_seats=500,
                status='active'
            ),
            Train(
                train_number='12346',
                train_name='Shatabdi Express',
                train_type='express',
                total_seats=400,
                status='active'
            ),
            Train(
                train_number='12347',
                train_name='Duronto Express',
                train_type='premium',
                total_seats=350,
                status='active'
            ),
            Train(
                train_number='12348',
                train_name='Local Passenger',
                train_type='local',
                total_seats=800,
                status='active'
            ),
            Train(
                train_number='12349',
                train_name='Garib Rath',
                train_type='express',
                total_seats=600,
                status='active'
            )
        ]
        
        for train in trains:
            db.session.add(train)
        
        # Create routes
        print("Creating routes...")
        routes = [
            Route(
                route_name='Delhi-Mumbai Route',
                source_station='New Delhi',
                destination_station='Mumbai Central',
                distance_km=1384.00,
                duration_hours=16.50,
                status='active'
            ),
            Route(
                route_name='Mumbai-Chennai Route',
                source_station='Mumbai Central',
                destination_station='Chennai Central',
                distance_km=1279.00,
                duration_hours=15.00,
                status='active'
            ),
            Route(
                route_name='Delhi-Kolkata Route',
                source_station='New Delhi',
                destination_station='Howrah',
                distance_km=1441.00,
                duration_hours=17.00,
                status='active'
            ),
            Route(
                route_name='Bangalore-Hyderabad Route',
                source_station='Bangalore City',
                destination_station='Hyderabad',
                distance_km=569.00,
                duration_hours=8.50,
                status='active'
            ),
            Route(
                route_name='Delhi-Jaipur Route',
                source_station='New Delhi',
                destination_station='Jaipur',
                distance_km=308.00,
                duration_hours=5.00,
                status='active'
            )
        ]
        
        for route in routes:
            db.session.add(route)
        
        db.session.commit()
        
        # Create schedules
        print("Creating schedules...")
        schedules = [
            Schedule(
                train_id=1,
                route_id=1,
                departure_time=datetime.strptime('16:00:00', '%H:%M:%S').time(),
                arrival_time=datetime.strptime('08:30:00', '%H:%M:%S').time(),
                frequency='daily',
                base_fare=1500.00,
                status='active'
            ),
            Schedule(
                train_id=2,
                route_id=2,
                departure_time=datetime.strptime('06:00:00', '%H:%M:%S').time(),
                arrival_time=datetime.strptime('21:00:00', '%H:%M:%S').time(),
                frequency='daily',
                base_fare=1200.00,
                status='active'
            ),
            Schedule(
                train_id=3,
                route_id=3,
                departure_time=datetime.strptime('22:30:00', '%H:%M:%S').time(),
                arrival_time=datetime.strptime('15:30:00', '%H:%M:%S').time(),
                frequency='daily',
                base_fare=1800.00,
                status='active'
            ),
            Schedule(
                train_id=4,
                route_id=4,
                departure_time=datetime.strptime('07:00:00', '%H:%M:%S').time(),
                arrival_time=datetime.strptime('15:30:00', '%H:%M:%S').time(),
                frequency='daily',
                base_fare=500.00,
                status='active'
            ),
            Schedule(
                train_id=5,
                route_id=5,
                departure_time=datetime.strptime('10:00:00', '%H:%M:%S').time(),
                arrival_time=datetime.strptime('15:00:00', '%H:%M:%S').time(),
                frequency='daily',
                base_fare=300.00,
                status='active'
            )
        ]
        
        for schedule in schedules:
            db.session.add(schedule)
        
        db.session.commit()
        
        # Create sample seats for the first schedule
        print("Creating sample seats...")
        today = date.today()
        for i in range(7):
            journey_date = today + timedelta(days=i)
            
            # Create 50 seats per day for the first schedule
            for seat_num in range(1, 51):
                seat_type = 'AC' if seat_num <= 20 else 'sleeper' if seat_num <= 40 else 'general'
                seat = Seat(
                    schedule_id=1,
                    journey_date=journey_date,
                    seat_number=f'S{seat_num}',
                    seat_type=seat_type,
                    is_available=True
                )
                db.session.add(seat)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("SUCCESS: Database seeded successfully!")
        print("="*60)
        print("\nSample Login Credentials:")
        print("-" * 60)
        print("Admin Account:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nUser Accounts:")
        print("  Username: john_doe")
        print("  Password: password123")
        print("\n  Username: jane_smith")
        print("  Password: password123")
        print("-" * 60)
        print("\nYou can now access the application at http://localhost:5000")
        print("="*60 + "\n")


if __name__ == '__main__':
    seed_database()
