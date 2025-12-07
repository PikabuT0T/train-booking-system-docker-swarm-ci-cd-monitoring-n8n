"""
Tests for Seat Routes (/api/seats)
"""
import pytest
from datetime import date, timedelta
from conftest import login_admin, login_regular_user


class TestGetAvailableSeats:
    """Test getting available seats (public access)"""
    
    def test_get_available_seats(self, client, init_database):
        """Test getting available seats for schedule and date"""
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.get(f'/api/seats/?schedule_id=1&journey_date={future_date}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'available_seats' in data
        assert 'occupied_seats' in data
        assert 'total_available' in data
        assert 'total_occupied' in data
    
    def test_get_seats_missing_schedule_id(self, client, init_database):
        """Test getting seats without schedule_id"""
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.get(f'/api/seats/?journey_date={future_date}')
        
        assert response.status_code == 400
        assert 'schedule_id' in response.get_json()['error']
    
    def test_get_seats_missing_journey_date(self, client, init_database):
        """Test getting seats without journey_date"""
        response = client.get('/api/seats/?schedule_id=1')
        
        assert response.status_code == 400
        assert 'journey_date' in response.get_json()['error']
    
    def test_get_seats_invalid_date_format(self, client, init_database):
        """Test getting seats with invalid date format"""
        response = client.get('/api/seats/?schedule_id=1&journey_date=invalid')
        
        assert response.status_code == 400
        assert 'Invalid date format' in response.get_json()['error']


class TestCreateSeat:
    """Test creating seats (admin only)"""
    
    def test_create_seat_as_admin(self, client, init_database):
        """Test creating seat as admin"""
        login_admin(client)
        
        future_date = (date.today() + timedelta(days=14)).isoformat()
        
        response = client.post('/api/seats/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'seat_number': 'B1',
            'seat_type': 'sleeper'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Seat created successfully'
        assert data['seat']['seat_number'] == 'B1'
        assert data['seat']['is_available'] is True
    
    def test_create_seat_as_user(self, client, init_database):
        """Test creating seat as regular user (should fail)"""
        login_regular_user(client)
        
        future_date = (date.today() + timedelta(days=14)).isoformat()
        
        response = client.post('/api/seats/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'seat_number': 'B2',
            'seat_type': 'AC'
        })
        
        assert response.status_code == 403
    
    def test_create_seat_missing_fields(self, client, init_database):
        """Test creating seat with missing fields"""
        login_admin(client)
        
        response = client.post('/api/seats/', json={
            'schedule_id': 1
        })
        
        assert response.status_code == 400
        assert 'is required' in response.get_json()['error']
    
    def test_create_seat_invalid_schedule(self, client, init_database):
        """Test creating seat for non-existent schedule"""
        login_admin(client)
        
        future_date = (date.today() + timedelta(days=14)).isoformat()
        
        response = client.post('/api/seats/', json={
            'schedule_id': 9999,
            'journey_date': future_date,
            'seat_number': 'C1',
            'seat_type': 'general'
        })
        
        assert response.status_code == 404
        assert 'Schedule not found' in response.get_json()['error']
    
    def test_create_duplicate_seat(self, client, init_database):
        """Test creating duplicate seat"""
        login_admin(client)
        
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        # Try to create seat with same number that already exists in fixtures
        response = client.post('/api/seats/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'seat_number': 'A1',  # Already exists from init_database
            'seat_type': 'AC'
        })
        
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']


class TestCreateBulkSeats:
    """Test bulk seat creation (admin only)"""
    
    def test_create_bulk_seats_as_admin(self, client, init_database):
        """Test bulk seat creation as admin"""
        login_admin(client)
        
        future_date = (date.today() + timedelta(days=21)).isoformat()
        
        response = client.post('/api/seats/bulk', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'seats': [
                {'seat_number': 'C1', 'seat_type': 'sleeper'},
                {'seat_number': 'C2', 'seat_type': 'sleeper'},
                {'seat_number': 'C3', 'seat_type': 'sleeper'}
            ]
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert '3 seats created' in data['message']
        assert len(data['seats']) == 3
    
    def test_create_bulk_seats_as_user(self, client, init_database):
        """Test bulk seat creation as regular user"""
        login_regular_user(client)
        
        future_date = (date.today() + timedelta(days=21)).isoformat()
        
        response = client.post('/api/seats/bulk', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'seats': [
                {'seat_number': 'D1', 'seat_type': 'general'}
            ]
        })
        
        assert response.status_code == 403
    
    def test_create_bulk_seats_missing_fields(self, client, init_database):
        """Test bulk creation with missing fields"""
        login_admin(client)
        
        response = client.post('/api/seats/bulk', json={
            'schedule_id': 1
        })
        
        assert response.status_code == 400
    
    def test_create_bulk_seats_invalid_schedule(self, client, init_database):
        """Test bulk creation with non-existent schedule"""
        login_admin(client)
        
        future_date = (date.today() + timedelta(days=21)).isoformat()
        
        response = client.post('/api/seats/bulk', json={
            'schedule_id': 9999,
            'journey_date': future_date,
            'seats': [
                {'seat_number': 'E1', 'seat_type': 'AC'}
            ]
        })
        
        assert response.status_code == 404


class TestUpdateSeat:
    """Test updating seats (admin only)"""
    
    def test_update_seat_as_admin(self, client, init_database, app):
        """Test updating seat as admin"""
        login_admin(client)
        
        # Get a seat ID from the database
        with app.app_context():
            from models import Seat
            seat = Seat.query.first()
            seat_id = seat.id
        
        response = client.put(f'/api/seats/{seat_id}', json={
            'is_available': False,
            'seat_type': 'first_class'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['seat']['is_available'] is False
        assert data['seat']['seat_type'] == 'first_class'
    
    def test_update_seat_as_user(self, client, init_database, app):
        """Test updating seat as regular user"""
        login_regular_user(client)
        
        with app.app_context():
            from models import Seat
            seat = Seat.query.first()
            seat_id = seat.id
        
        response = client.put(f'/api/seats/{seat_id}', json={
            'is_available': False
        })
        
        assert response.status_code == 403
    
    def test_update_seat_not_found(self, client, init_database):
        """Test updating non-existent seat"""
        login_admin(client)
        
        response = client.put('/api/seats/9999', json={
            'is_available': False
        })
        
        assert response.status_code == 404


class TestDeleteSeat:
    """Test deleting seats (admin only)"""
    
    def test_delete_seat_as_admin(self, client, init_database):
        """Test deleting seat as admin"""
        login_admin(client)
        
        # Create a seat to delete
        future_date = (date.today() + timedelta(days=30)).isoformat()
        create_response = client.post('/api/seats/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'seat_number': 'DELETE1',
            'seat_type': 'general'
        })
        seat_id = create_response.get_json()['seat']['id']
        
        response = client.delete(f'/api/seats/{seat_id}')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']
    
    def test_delete_seat_as_user(self, client, init_database, app):
        """Test deleting seat as regular user"""
        login_regular_user(client)
        
        with app.app_context():
            from models import Seat
            seat = Seat.query.first()
            seat_id = seat.id
        
        response = client.delete(f'/api/seats/{seat_id}')
        
        assert response.status_code == 403
    
    def test_delete_seat_not_found(self, client, init_database):
        """Test deleting non-existent seat"""
        login_admin(client)
        
        response = client.delete('/api/seats/9999')
        
        assert response.status_code == 404
