"""
Tests for Ticket Routes (/api/tickets)
"""
import pytest
from datetime import date, timedelta
from conftest import login_admin, login_regular_user


class TestBookTicket:
    """Test ticket booking"""
    
    def test_book_ticket_success(self, client, init_database):
        """Test successful ticket booking"""
        login_regular_user(client)
        
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'John Doe',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Ticket booked successfully'
        assert 'pnr_number' in data['ticket']
        assert data['ticket']['passenger_name'] == 'John Doe'
    
    def test_book_ticket_not_authenticated(self, client, init_database):
        """Test booking ticket without login"""
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'John Doe',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        
        assert response.status_code == 401
    
    def test_book_ticket_missing_fields(self, client, init_database):
        """Test booking with missing fields"""
        login_regular_user(client)
        
        response = client.post('/api/tickets/', json={
            'schedule_id': 1
        })
        
        assert response.status_code == 400
        assert 'is required' in response.get_json()['error']
    
    def test_book_ticket_invalid_schedule(self, client, init_database):
        """Test booking with non-existent schedule"""
        login_regular_user(client)
        
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.post('/api/tickets/', json={
            'schedule_id': 9999,
            'journey_date': future_date,
            'passenger_name': 'John Doe',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        
        assert response.status_code == 404
        assert 'Schedule not found' in response.get_json()['error']
    
    def test_book_ticket_past_date(self, client, init_database):
        """Test booking for past date"""
        login_regular_user(client)
        
        past_date = (date.today() - timedelta(days=1)).isoformat()
        
        response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': past_date,
            'passenger_name': 'John Doe',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        
        assert response.status_code == 400
        assert 'future' in response.get_json()['error'].lower()
    
    def test_book_ticket_invalid_date_format(self, client, init_database):
        """Test booking with invalid date format"""
        login_regular_user(client)
        
        response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': 'invalid-date',
            'passenger_name': 'John Doe',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        
        assert response.status_code == 400


class TestGetTickets:
    """Test getting tickets"""
    
    def test_get_user_tickets(self, client, init_database):
        """Test getting user's own tickets"""
        login_regular_user(client)
        
        # Book a ticket first
        future_date = (date.today() + timedelta(days=7)).isoformat()
        client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Test Passenger',
            'passenger_age': 25,
            'passenger_gender': 'female'
        })
        
        response = client.get('/api/tickets/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'tickets' in data
        assert 'count' in data
        assert data['count'] >= 1
    
    def test_get_tickets_not_authenticated(self, client, init_database):
        """Test getting tickets without login"""
        response = client.get('/api/tickets/')
        
        assert response.status_code == 401
    
    def test_admin_gets_all_tickets(self, client, init_database):
        """Test admin can see all tickets"""
        # User books a ticket
        login_regular_user(client)
        future_date = (date.today() + timedelta(days=7)).isoformat()
        client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'User Ticket',
            'passenger_age': 25,
            'passenger_gender': 'male'
        })
        client.post('/api/auth/logout')
        
        # Admin checks tickets
        login_admin(client)
        response = client.get('/api/tickets/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1


class TestGetTicketById:
    """Test getting ticket by ID"""
    
    def test_get_own_ticket(self, client, init_database):
        """Test user can get their own ticket"""
        login_regular_user(client)
        
        # Book a ticket
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Test',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        
        response = client.get(f'/api/tickets/{ticket_id}')
        
        assert response.status_code == 200
        assert response.get_json()['ticket']['id'] == ticket_id
    
    def test_get_ticket_not_found(self, client, init_database):
        """Test getting non-existent ticket"""
        login_regular_user(client)
        
        response = client.get('/api/tickets/9999')
        
        assert response.status_code == 404
    
    def test_user_cannot_access_others_ticket(self, client, init_database, app):
        """Test user cannot access another user's ticket"""
        # Admin books a ticket
        login_admin(client)
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Admin Ticket',
            'passenger_age': 35,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        client.post('/api/auth/logout')
        
        # Regular user tries to access it
        login_regular_user(client)
        response = client.get(f'/api/tickets/{ticket_id}')
        
        assert response.status_code == 403
        assert 'Access denied' in response.get_json()['error']


class TestGetTicketByPnr:
    """Test getting ticket by PNR (public access)"""
    
    def test_get_ticket_by_pnr(self, client, init_database):
        """Test getting ticket by PNR number"""
        login_regular_user(client)
        
        # Book a ticket
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'PNR Test',
            'passenger_age': 28,
            'passenger_gender': 'female'
        })
        pnr = book_response.get_json()['ticket']['pnr_number']
        client.post('/api/auth/logout')
        
        # Get ticket by PNR without auth
        response = client.get(f'/api/tickets/pnr/{pnr}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ticket']['pnr_number'] == pnr
    
    def test_get_ticket_by_invalid_pnr(self, client, init_database):
        """Test getting ticket with invalid PNR"""
        response = client.get('/api/tickets/pnr/INVALIDPNR')
        
        assert response.status_code == 404


class TestCancelTicket:
    """Test ticket cancellation"""
    
    def test_cancel_own_ticket(self, client, init_database):
        """Test user can cancel their own ticket"""
        login_regular_user(client)
        
        # Book a ticket
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Cancel Test',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        
        response = client.put(f'/api/tickets/{ticket_id}/cancel')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ticket']['status'] == 'cancelled'
    
    def test_cancel_already_cancelled(self, client, init_database):
        """Test cancelling already cancelled ticket"""
        login_regular_user(client)
        
        # Book and cancel a ticket
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Double Cancel',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        client.put(f'/api/tickets/{ticket_id}/cancel')
        
        # Try to cancel again
        response = client.put(f'/api/tickets/{ticket_id}/cancel')
        
        assert response.status_code == 400
        assert 'already cancelled' in response.get_json()['error']
    
    def test_cancel_ticket_not_found(self, client, init_database):
        """Test cancelling non-existent ticket"""
        login_regular_user(client)
        
        response = client.put('/api/tickets/9999/cancel')
        
        assert response.status_code == 404
    
    def test_user_cannot_cancel_others_ticket(self, client, init_database):
        """Test user cannot cancel another user's ticket"""
        # Admin books a ticket
        login_admin(client)
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Admin Ticket',
            'passenger_age': 35,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        client.post('/api/auth/logout')
        
        # Regular user tries to cancel
        login_regular_user(client)
        response = client.put(f'/api/tickets/{ticket_id}/cancel')
        
        assert response.status_code == 403


class TestDeleteTicket:
    """Test ticket deletion (admin only)"""
    
    def test_admin_delete_ticket(self, client, init_database):
        """Test admin can delete ticket"""
        login_regular_user(client)
        
        # Book a ticket
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'Delete Test',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        client.post('/api/auth/logout')
        
        # Admin deletes it
        login_admin(client)
        response = client.delete(f'/api/tickets/{ticket_id}')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']
    
    def test_user_cannot_delete_ticket(self, client, init_database):
        """Test regular user cannot delete ticket"""
        login_regular_user(client)
        
        # Book a ticket
        future_date = (date.today() + timedelta(days=7)).isoformat()
        book_response = client.post('/api/tickets/', json={
            'schedule_id': 1,
            'journey_date': future_date,
            'passenger_name': 'No Delete',
            'passenger_age': 30,
            'passenger_gender': 'male'
        })
        ticket_id = book_response.get_json()['ticket']['id']
        
        response = client.delete(f'/api/tickets/{ticket_id}')
        
        assert response.status_code == 403
