"""
Authentication Routes - Login, Register, Logout (Session-based)
"""
from flask import Blueprint, request, jsonify, session
from models import db, User
from functools import wraps

auth_bp = Blueprint('auth', __name__)


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


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone=data.get('phone'),
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user information"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            }), 200
    
    return jsonify({'authenticated': False}), 200
