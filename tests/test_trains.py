"""
Tests for Train Routes (/api/trains)
"""
import pytest
from conftest import login_admin, login_regular_user


class TestGetTrains:
    """Test getting trains (public access)"""
    
    def test_get_all_trains(self, client, init_database):
        """Test getting all trains"""
        response = client.get('/api/trains/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'trains' in data
        assert 'count' in data
        assert data['count'] >= 1
    
    def test_get_all_trains_empty(self, client, app):
        """Test getting trains when none exist"""
        response = client.get('/api/trains/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['trains'] == []
        assert data['count'] == 0
    
    def test_filter_trains_by_status(self, client, init_database):
        """Test filtering trains by status"""
        response = client.get('/api/trains/?status=active')
        
        assert response.status_code == 200
        data = response.get_json()
        for train in data['trains']:
            assert train['status'] == 'active'
    
    def test_filter_trains_by_type(self, client, init_database):
        """Test filtering trains by type"""
        response = client.get('/api/trains/?train_type=express')
        
        assert response.status_code == 200
        data = response.get_json()
        for train in data['trains']:
            assert train['train_type'] == 'express'


class TestGetTrain:
    """Test getting single train"""
    
    def test_get_train_by_id(self, client, init_database):
        """Test getting train by ID"""
        response = client.get('/api/trains/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['train']['train_number'] == 'EXP001'
    
    def test_get_train_not_found(self, client, init_database):
        """Test getting non-existent train"""
        response = client.get('/api/trains/9999')
        
        assert response.status_code == 404
        assert 'Train not found' in response.get_json()['error']


class TestCreateTrain:
    """Test creating trains (admin only)"""
    
    def test_create_train_as_admin(self, client, init_database):
        """Test creating train as admin"""
        login_admin(client)
        
        response = client.post('/api/trains/', json={
            'train_number': 'NEW001',
            'train_name': 'New Express',
            'train_type': 'superfast',
            'total_seats': 200
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Train created successfully'
        assert data['train']['train_number'] == 'NEW001'
    
    def test_create_train_as_user(self, client, init_database):
        """Test creating train as regular user (should fail)"""
        login_regular_user(client)
        
        response = client.post('/api/trains/', json={
            'train_number': 'NEW002',
            'train_name': 'Another Train',
            'train_type': 'local',
            'total_seats': 150
        })
        
        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']
    
    def test_create_train_not_authenticated(self, client, init_database):
        """Test creating train without login"""
        response = client.post('/api/trains/', json={
            'train_number': 'NEW003',
            'train_name': 'Test Train',
            'train_type': 'express',
            'total_seats': 100
        })
        
        assert response.status_code == 401
    
    def test_create_train_missing_fields(self, client, init_database):
        """Test creating train with missing fields"""
        login_admin(client)
        
        response = client.post('/api/trains/', json={
            'train_number': 'NEW004'
        })
        
        assert response.status_code == 400
        assert 'is required' in response.get_json()['error']
    
    def test_create_train_duplicate_number(self, client, init_database):
        """Test creating train with existing number"""
        login_admin(client)
        
        response = client.post('/api/trains/', json={
            'train_number': 'EXP001',  # Already exists
            'train_name': 'Duplicate Train',
            'train_type': 'express',
            'total_seats': 100
        })
        
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']


class TestUpdateTrain:
    """Test updating trains (admin only)"""
    
    def test_update_train_as_admin(self, client, init_database):
        """Test updating train as admin"""
        login_admin(client)
        
        response = client.put('/api/trains/1', json={
            'train_name': 'Updated Express',
            'total_seats': 150
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['train']['train_name'] == 'Updated Express'
        assert data['train']['total_seats'] == 150
    
    def test_update_train_as_user(self, client, init_database):
        """Test updating train as regular user"""
        login_regular_user(client)
        
        response = client.put('/api/trains/1', json={
            'train_name': 'Hacked Train'
        })
        
        assert response.status_code == 403
    
    def test_update_train_not_found(self, client, init_database):
        """Test updating non-existent train"""
        login_admin(client)
        
        response = client.put('/api/trains/9999', json={
            'train_name': 'Ghost Train'
        })
        
        assert response.status_code == 404


class TestDeleteTrain:
    """Test deleting trains (admin only)"""
    
    def test_delete_train_as_admin(self, client, init_database):
        """Test deleting train as admin"""
        login_admin(client)
        
        # First create a train to delete
        client.post('/api/trains/', json={
            'train_number': 'DEL001',
            'train_name': 'To Delete',
            'train_type': 'local',
            'total_seats': 50
        })
        
        response = client.delete('/api/trains/2')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']
    
    def test_delete_train_as_user(self, client, init_database):
        """Test deleting train as regular user"""
        login_regular_user(client)
        
        response = client.delete('/api/trains/1')
        
        assert response.status_code == 403
    
    def test_delete_train_not_found(self, client, init_database):
        """Test deleting non-existent train"""
        login_admin(client)
        
        response = client.delete('/api/trains/9999')
        
        assert response.status_code == 404


class TestSearchTrains:
    """Test train search"""
    
    def test_search_trains_by_number(self, client, init_database):
        """Test searching trains by number"""
        response = client.get('/api/trains/search?q=EXP')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_search_trains_by_name(self, client, init_database):
        """Test searching trains by name"""
        response = client.get('/api/trains/search?q=Express')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_search_trains_no_query(self, client, init_database):
        """Test search without query"""
        response = client.get('/api/trains/search')
        
        assert response.status_code == 400
        assert 'Search query is required' in response.get_json()['error']
    
    def test_search_trains_no_results(self, client, init_database):
        """Test search with no matching results"""
        response = client.get('/api/trains/search?q=NONEXISTENT')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 0
