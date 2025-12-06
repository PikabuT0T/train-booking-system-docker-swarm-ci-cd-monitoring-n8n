"""
Train Management Routes - CRUD operations for trains
"""
from flask import Blueprint, request, jsonify, session
from models import db, User, Train
from routes.auth_helpers import login_required, admin_required

train_bp = Blueprint('trains', __name__)


@train_bp.route('/', methods=['GET'])
def get_all_trains():
    """Get all trains (public access)"""
    try:
        # Optional filters
        status = request.args.get('status')
        train_type = request.args.get('train_type')
        
        query = Train.query
        
        if status:
            query = query.filter_by(status=status)
        if train_type:
            query = query.filter_by(train_type=train_type)
        
        trains = query.all()
        
        return jsonify({
            'trains': [train.to_dict() for train in trains],
            'count': len(trains)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@train_bp.route('/<int:train_id>', methods=['GET'])
def get_train(train_id):
    """Get train by ID (public access)"""
    try:
        train = Train.query.get(train_id)
        
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        return jsonify({
            'train': train.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@train_bp.route('/', methods=['POST'])
@admin_required
def create_train():
    """Create new train (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['train_number', 'train_name', 'train_type', 'total_seats']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if train number already exists
        if Train.query.filter_by(train_number=data['train_number']).first():
            return jsonify({'error': 'Train number already exists'}), 400
        
        # Create new train
        train = Train(
            train_number=data['train_number'],
            train_name=data['train_name'],
            train_type=data['train_type'],
            total_seats=data['total_seats'],
            status=data.get('status', 'active')
        )
        
        db.session.add(train)
        db.session.commit()
        
        return jsonify({
            'message': 'Train created successfully',
            'train': train.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@train_bp.route('/<int:train_id>', methods=['PUT'])
@admin_required
def update_train(train_id):
    """Update train information (admin only)"""
    try:
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'train_name' in data:
            train.train_name = data['train_name']
        if 'train_type' in data:
            train.train_type = data['train_type']
        if 'total_seats' in data:
            train.total_seats = data['total_seats']
        if 'status' in data:
            train.status = data['status']
        if 'train_number' in data:
            # Check uniqueness
            existing = Train.query.filter_by(train_number=data['train_number']).first()
            if existing and existing.id != train_id:
                return jsonify({'error': 'Train number already exists'}), 400
            train.train_number = data['train_number']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Train updated successfully',
            'train': train.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@train_bp.route('/<int:train_id>', methods=['DELETE'])
@admin_required
def delete_train(train_id):
    """Delete train (admin only)"""
    try:
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        db.session.delete(train)
        db.session.commit()
        
        return jsonify({
            'message': 'Train deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@train_bp.route('/search', methods=['GET'])
def search_trains():
    """Search trains by train number or name"""
    try:
        query_str = request.args.get('q', '')
        
        if not query_str:
            return jsonify({'error': 'Search query is required'}), 400
        
        trains = Train.query.filter(
            (Train.train_number.like(f'%{query_str}%')) |
            (Train.train_name.like(f'%{query_str}%'))
        ).all()
        
        return jsonify({
            'trains': [train.to_dict() for train in trains],
            'count': len(trains)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
