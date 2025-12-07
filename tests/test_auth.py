"""
Tests for Authentication Routes (/api/auth)
"""
import pytest
from models import User, db


class TestAuthRegister:
    """Test user registration"""
    
    def test_register_success(self, client, app):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123',
            'full_name': 'New User',
            'phone': '1111111111'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@test.com'
        assert data['user']['role'] == 'user'
        assert 'password' not in data['user']
    
    def test_register_missing_username(self, client, app):
        """Test registration with missing username"""
        response = client.post('/api/auth/register', json={
            'email': 'test@test.com',
            'password': 'password123',
            'full_name': 'Test User'
        })
        
        assert response.status_code == 400
        assert 'username is required' in response.get_json()['error']
    
    def test_register_missing_email(self, client, app):
        """Test registration with missing email"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'password123',
            'full_name': 'Test User'
        })
        
        assert response.status_code == 400
        assert 'email is required' in response.get_json()['error']
    
    def test_register_missing_password(self, client, app):
        """Test registration with missing password"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'full_name': 'Test User'
        })
        
        assert response.status_code == 400
        assert 'password is required' in response.get_json()['error']
    
    def test_register_duplicate_username(self, client, init_database):
        """Test registration with existing username"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',  # Already exists
            'email': 'different@test.com',
            'password': 'password123',
            'full_name': 'Another User'
        })
        
        assert response.status_code == 400
        assert 'Username already exists' in response.get_json()['error']
    
    def test_register_duplicate_email(self, client, init_database):
        """Test registration with existing email"""
        response = client.post('/api/auth/register', json={
            'username': 'differentuser',
            'email': 'testuser@test.com',  # Already exists
            'password': 'password123',
            'full_name': 'Another User'
        })
        
        assert response.status_code == 400
        assert 'Email already exists' in response.get_json()['error']


class TestAuthLogin:
    """Test user login"""
    
    def test_login_success(self, client, init_database):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'userpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert data['user']['username'] == 'testuser'
    
    def test_login_admin(self, client, init_database):
        """Test admin login"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'admin'
    
    def test_login_invalid_username(self, client, init_database):
        """Test login with invalid username"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        assert 'Invalid username or password' in response.get_json()['error']
    
    def test_login_invalid_password(self, client, init_database):
        """Test login with wrong password"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'Invalid username or password' in response.get_json()['error']
    
    def test_login_missing_credentials(self, client, app):
        """Test login without credentials"""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == 400
        assert 'required' in response.get_json()['error']


class TestAuthLogout:
    """Test user logout"""
    
    def test_logout_success(self, client, init_database):
        """Test successful logout"""
        # Login first
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'userpass123'
        })
        
        # Logout
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Logout successful'
    
    def test_logout_without_login(self, client, app):
        """Test logout without being logged in"""
        response = client.post('/api/auth/logout')
        
        # Should still return success (clearing empty session)
        assert response.status_code == 200


class TestAuthMe:
    """Test get current user"""
    
    def test_get_current_user(self, client, init_database):
        """Test getting current user info"""
        # Login first
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'userpass123'
        })
        
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'testuser'
    
    def test_get_current_user_not_authenticated(self, client, app):
        """Test getting current user without login"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        assert 'Authentication required' in response.get_json()['error']


class TestAuthCheck:
    """Test authentication status check"""
    
    def test_check_authenticated(self, client, init_database):
        """Test check when authenticated"""
        # Login first
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'userpass123'
        })
        
        response = client.get('/api/auth/check')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['authenticated'] is True
        assert data['user']['username'] == 'testuser'
    
    def test_check_not_authenticated(self, client, app):
        """Test check when not authenticated"""
        response = client.get('/api/auth/check')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['authenticated'] is False
