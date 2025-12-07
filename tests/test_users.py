"""
Tests for User Routes (/api/users)
"""
import pytest
from conftest import login_admin, login_regular_user


class TestGetAllUsers:
    """Test getting all users (admin only)"""
    
    def test_get_all_users_as_admin(self, client, init_database):
        """Test admin can get all users"""
        login_admin(client)
        
        response = client.get('/api/users/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert len(data['users']) >= 2  # Admin and regular user
    
    def test_get_all_users_as_user(self, client, init_database):
        """Test regular user cannot get all users"""
        login_regular_user(client)
        
        response = client.get('/api/users/')
        
        assert response.status_code == 403
    
    def test_get_all_users_not_authenticated(self, client, init_database):
        """Test unauthenticated request"""
        response = client.get('/api/users/')
        
        assert response.status_code == 401


class TestGetUser:
    """Test getting single user"""
    
    def test_get_own_profile(self, client, init_database, app):
        """Test user can get their own profile"""
        login_regular_user(client)
        
        # Get user ID
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.get(f'/api/users/{user_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'testuser'
    
    def test_user_cannot_get_other_profile(self, client, init_database, app):
        """Test user cannot get another user's profile"""
        login_regular_user(client)
        
        # Get admin ID
        with app.app_context():
            from models import User
            admin = User.query.filter_by(username='admin').first()
            admin_id = admin.id
        
        response = client.get(f'/api/users/{admin_id}')
        
        assert response.status_code == 403
    
    def test_admin_can_get_any_profile(self, client, init_database, app):
        """Test admin can get any user's profile"""
        login_admin(client)
        
        # Get regular user ID
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.get(f'/api/users/{user_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'testuser'
    
    def test_get_user_not_found(self, client, init_database):
        """Test getting non-existent user"""
        login_admin(client)
        
        response = client.get('/api/users/9999')
        
        assert response.status_code == 404


class TestUpdateUser:
    """Test updating user"""
    
    def test_update_own_profile(self, client, init_database, app):
        """Test user can update their own profile"""
        login_regular_user(client)
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.put(f'/api/users/{user_id}', json={
            'full_name': 'Updated Name',
            'phone': '9999999999'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['full_name'] == 'Updated Name'
        assert data['user']['phone'] == '9999999999'
    
    def test_user_cannot_update_other_profile(self, client, init_database, app):
        """Test user cannot update another user's profile"""
        login_regular_user(client)
        
        with app.app_context():
            from models import User
            admin = User.query.filter_by(username='admin').first()
            admin_id = admin.id
        
        response = client.put(f'/api/users/{admin_id}', json={
            'full_name': 'Hacked Name'
        })
        
        assert response.status_code == 403
    
    def test_admin_can_update_any_profile(self, client, init_database, app):
        """Test admin can update any user's profile"""
        login_admin(client)
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.put(f'/api/users/{user_id}', json={
            'full_name': 'Admin Updated'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['full_name'] == 'Admin Updated'
    
    def test_admin_can_change_role(self, client, init_database, app):
        """Test admin can change user role"""
        login_admin(client)
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.put(f'/api/users/{user_id}', json={
            'role': 'admin'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'admin'
    
    def test_user_cannot_change_own_role(self, client, init_database, app):
        """Test regular user cannot change their own role"""
        login_regular_user(client)
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.put(f'/api/users/{user_id}', json={
            'role': 'admin'
        })
        
        # The update succeeds but role remains unchanged (non-admin can't change role)
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'user'
    
    def test_update_password(self, client, init_database, app):
        """Test user can update their password"""
        login_regular_user(client)
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.put(f'/api/users/{user_id}', json={
            'password': 'newpassword123'
        })
        
        assert response.status_code == 200
        
        # Logout and login with new password
        client.post('/api/auth/logout')
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'newpassword123'
        })
        
        assert login_response.status_code == 200
    
    def test_update_email_duplicate(self, client, init_database, app):
        """Test updating email to existing email fails"""
        login_regular_user(client)
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        response = client.put(f'/api/users/{user_id}', json={
            'email': 'admin@test.com'  # Admin's email
        })
        
        assert response.status_code == 400
        assert 'already in use' in response.get_json()['error']


class TestDeleteUser:
    """Test deleting user"""
    
    def test_delete_own_account(self, client, init_database, app):
        """Test user can delete their own account"""
        # Create a user to delete
        client.post('/api/auth/register', json={
            'username': 'todelete',
            'email': 'todelete@test.com',
            'password': 'password123',
            'full_name': 'To Delete'
        })
        
        client.post('/api/auth/login', json={
            'username': 'todelete',
            'password': 'password123'
        })
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='todelete').first()
            user_id = user.id
        
        response = client.delete(f'/api/users/{user_id}')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']
    
    def test_user_cannot_delete_other_account(self, client, init_database, app):
        """Test user cannot delete another user's account"""
        login_regular_user(client)
        
        with app.app_context():
            from models import User
            admin = User.query.filter_by(username='admin').first()
            admin_id = admin.id
        
        response = client.delete(f'/api/users/{admin_id}')
        
        assert response.status_code == 403
    
    def test_admin_can_delete_any_account(self, client, init_database, app):
        """Test admin can delete any user's account"""
        # Create a user to delete
        client.post('/api/auth/register', json={
            'username': 'admindelete',
            'email': 'admindelete@test.com',
            'password': 'password123',
            'full_name': 'Admin Delete'
        })
        
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='admindelete').first()
            user_id = user.id
        
        login_admin(client)
        response = client.delete(f'/api/users/{user_id}')
        
        assert response.status_code == 200
    
    def test_delete_user_not_found(self, client, init_database):
        """Test deleting non-existent user"""
        login_admin(client)
        
        response = client.delete('/api/users/9999')
        
        assert response.status_code == 404
