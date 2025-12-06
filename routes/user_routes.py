"""
User Management Routes - CRUD operations for users
"""
from flask import Blueprint, request, jsonify, session
from models import db, User
from routes.auth_helpers import login_required, admin_required, get_current_user_id

user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get user by ID"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        # Users can only view their own profile unless admin
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user profile"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        # Users can only update their own profile unless admin
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data:
            # Check email uniqueness
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        
        # Only admin can change role
        if 'role' in data and current_user.role == 'admin':
            user.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete user account"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        # Users can delete their own account or admin can delete any
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
