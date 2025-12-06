"""
Authentication helper functions and decorators
"""
from flask import session, jsonify
from functools import wraps
from models import User


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')


def get_current_user():
    """Get current user object from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None
