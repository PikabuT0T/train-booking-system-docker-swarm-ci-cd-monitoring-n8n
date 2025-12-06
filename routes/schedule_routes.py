"""
Schedule Management Routes - CRUD operations for schedules
"""
from flask import Blueprint, request, jsonify, session
from models import db, User, Schedule, Train, Route
from routes.auth_helpers import login_required, admin_required
from datetime import datetime

schedule_bp = Blueprint('schedules', __name__)


@schedule_bp.route('/', methods=['GET'])
def get_all_schedules():
    """Get all schedules (public access)"""
    try:
        # Optional filters
        train_id = request.args.get('train_id', type=int)
        route_id = request.args.get('route_id', type=int)
        status = request.args.get('status')
        
        query = Schedule.query
        
        if train_id:
            query = query.filter_by(train_id=train_id)
        if route_id:
            query = query.filter_by(route_id=route_id)
        if status:
            query = query.filter_by(status=status)
        
        schedules = query.all()
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules],
            'count': len(schedules)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Get schedule by ID (public access)"""
    try:
        schedule = Schedule.query.get(schedule_id)
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        return jsonify({
            'schedule': schedule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/', methods=['POST'])
@admin_required
def create_schedule():
    """Create new schedule (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['train_id', 'route_id', 'departure_time', 
                          'arrival_time', 'frequency', 'base_fare']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify train and route exist
        train = Train.query.get(data['train_id'])
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        route = Route.query.get(data['route_id'])
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        # Parse times
        departure_time = datetime.strptime(data['departure_time'], '%H:%M:%S').time()
        arrival_time = datetime.strptime(data['arrival_time'], '%H:%M:%S').time()
        
        # Create new schedule
        schedule = Schedule(
            train_id=data['train_id'],
            route_id=data['route_id'],
            departure_time=departure_time,
            arrival_time=arrival_time,
            frequency=data['frequency'],
            base_fare=data['base_fare'],
            status=data.get('status', 'active')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
        
    except ValueError as ve:
        return jsonify({'error': 'Invalid time format. Use HH:MM:SS'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@admin_required
def update_schedule(schedule_id):
    """Update schedule information (admin only)"""
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'departure_time' in data:
            schedule.departure_time = datetime.strptime(data['departure_time'], '%H:%M:%S').time()
        if 'arrival_time' in data:
            schedule.arrival_time = datetime.strptime(data['arrival_time'], '%H:%M:%S').time()
        if 'frequency' in data:
            schedule.frequency = data['frequency']
        if 'base_fare' in data:
            schedule.base_fare = data['base_fare']
        if 'status' in data:
            schedule.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule updated successfully',
            'schedule': schedule.to_dict()
        }), 200
        
    except ValueError as ve:
        return jsonify({'error': 'Invalid time format. Use HH:MM:SS'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@admin_required
def delete_schedule(schedule_id):
    """Delete schedule (admin only)"""
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/search', methods=['GET'])
def search_schedules():
    """Search schedules by source and destination"""
    try:
        source = request.args.get('source')
        destination = request.args.get('destination')
        
        if not source or not destination:
            return jsonify({'error': 'Source and destination are required'}), 400
        
        schedules = Schedule.query.join(Route).filter(
            Route.source_station.like(f'%{source}%'),
            Route.destination_station.like(f'%{destination}%'),
            Schedule.status == 'active'
        ).all()
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules],
            'count': len(schedules)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
