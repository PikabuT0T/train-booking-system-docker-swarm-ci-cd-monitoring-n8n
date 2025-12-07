"""
Tests for Route Routes (/api/routes)
"""
import pytest
from conftest import login_admin, login_regular_user


class TestGetRoutes:
    """Test getting routes (public access)"""
    
    def test_get_all_routes(self, client, init_database):
        """Test getting all routes"""
        response = client.get('/api/routes/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'routes' in data
        assert 'count' in data
        assert data['count'] >= 1
    
    def test_filter_routes_by_status(self, client, init_database):
        """Test filtering routes by status"""
        response = client.get('/api/routes/?status=active')
        
        assert response.status_code == 200
        data = response.get_json()
        for route in data['routes']:
            assert route['status'] == 'active'
    
    def test_filter_routes_by_source(self, client, init_database):
        """Test filtering routes by source station"""
        response = client.get('/api/routes/?source=City A')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_filter_routes_by_destination(self, client, init_database):
        """Test filtering routes by destination"""
        response = client.get('/api/routes/?destination=City B')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1


class TestGetRoute:
    """Test getting single route"""
    
    def test_get_route_by_id(self, client, init_database):
        """Test getting route by ID"""
        response = client.get('/api/routes/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['route']['route_name'] == 'City A to City B'
    
    def test_get_route_not_found(self, client, init_database):
        """Test getting non-existent route"""
        response = client.get('/api/routes/9999')
        
        assert response.status_code == 404
        assert 'Route not found' in response.get_json()['error']


class TestCreateRoute:
    """Test creating routes (admin only)"""
    
    def test_create_route_as_admin(self, client, init_database):
        """Test creating route as admin"""
        login_admin(client)
        
        response = client.post('/api/routes/', json={
            'route_name': 'New Route',
            'source_station': 'Station X',
            'destination_station': 'Station Y',
            'distance_km': 300.5,
            'duration_hours': 4.5
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Route created successfully'
        assert data['route']['route_name'] == 'New Route'
    
    def test_create_route_as_user(self, client, init_database):
        """Test creating route as regular user (should fail)"""
        login_regular_user(client)
        
        response = client.post('/api/routes/', json={
            'route_name': 'Unauthorized Route',
            'source_station': 'Station A',
            'destination_station': 'Station B',
            'distance_km': 100,
            'duration_hours': 2
        })
        
        assert response.status_code == 403
    
    def test_create_route_missing_fields(self, client, init_database):
        """Test creating route with missing fields"""
        login_admin(client)
        
        response = client.post('/api/routes/', json={
            'route_name': 'Incomplete Route'
        })
        
        assert response.status_code == 400
        assert 'is required' in response.get_json()['error']


class TestUpdateRoute:
    """Test updating routes (admin only)"""
    
    def test_update_route_as_admin(self, client, init_database):
        """Test updating route as admin"""
        login_admin(client)
        
        response = client.put('/api/routes/1', json={
            'route_name': 'Updated Route Name',
            'distance_km': 550.0
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['route']['route_name'] == 'Updated Route Name'
        assert data['route']['distance_km'] == 550.0
    
    def test_update_route_as_user(self, client, init_database):
        """Test updating route as regular user"""
        login_regular_user(client)
        
        response = client.put('/api/routes/1', json={
            'route_name': 'Hacked Route'
        })
        
        assert response.status_code == 403
    
    def test_update_route_not_found(self, client, init_database):
        """Test updating non-existent route"""
        login_admin(client)
        
        response = client.put('/api/routes/9999', json={
            'route_name': 'Ghost Route'
        })
        
        assert response.status_code == 404


class TestDeleteRoute:
    """Test deleting routes (admin only)"""
    
    def test_delete_route_as_admin(self, client, init_database):
        """Test deleting route as admin"""
        login_admin(client)
        
        # First create a route to delete
        create_response = client.post('/api/routes/', json={
            'route_name': 'To Delete',
            'source_station': 'Delete A',
            'destination_station': 'Delete B',
            'distance_km': 100,
            'duration_hours': 1.5
        })
        route_id = create_response.get_json()['route']['id']
        
        response = client.delete(f'/api/routes/{route_id}')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']
    
    def test_delete_route_as_user(self, client, init_database):
        """Test deleting route as regular user"""
        login_regular_user(client)
        
        response = client.delete('/api/routes/1')
        
        assert response.status_code == 403
    
    def test_delete_route_not_found(self, client, init_database):
        """Test deleting non-existent route"""
        login_admin(client)
        
        response = client.delete('/api/routes/9999')
        
        assert response.status_code == 404
