"""
Seat Management Routes - CRUD operations for seats
"""
from flask import Blueprint, request, jsonify, session
from models import db, User, Seat, Schedule
from routes.auth_helpers import login_required, admin_required
from datetime import datetime

seat_bp = Blueprint('seats', __name__)


@seat_bp.route('/', methods=['GET'])
def get_available_seats():
    """Get available seats for a schedule and date"""
    try:
        schedule_id = request.args.get('schedule_id', type=int)
        journey_date = request.args.get('journey_date')
        
        if not schedule_id or not journey_date:
            return jsonify({'error': 'schedule_id and journey_date are required'}), 400
        
        # Parse date
        try:
            journey_date_obj = datetime.strptime(journey_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get seats
        seats = Seat.query.filter_by(
            schedule_id=schedule_id,
            journey_date=journey_date_obj
        ).all()
        
        available = [seat.to_dict() for seat in seats if seat.is_available]
        occupied = [seat.to_dict() for seat in seats if not seat.is_available]
        
        return jsonify({
            'available_seats': available,
            'occupied_seats': occupied,
            'total_available': len(available),
            'total_occupied': len(occupied)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@seat_bp.route('/', methods=['POST'])
@admin_required
def create_seat():
    """Create/initialize seats for a schedule (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['schedule_id', 'journey_date', 'seat_number', 'seat_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify schedule exists
        schedule = Schedule.query.get(data['schedule_id'])
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Parse date
        journey_date = datetime.strptime(data['journey_date'], '%Y-%m-%d').date()
        
        # Check if seat already exists
        existing_seat = Seat.query.filter_by(
            schedule_id=data['schedule_id'],
            journey_date=journey_date,
            seat_number=data['seat_number']
        ).first()
        
        if existing_seat:
            return jsonify({'error': 'Seat already exists'}), 400
        
        # Create new seat
        seat = Seat(
            schedule_id=data['schedule_id'],
            journey_date=journey_date,
            seat_number=data['seat_number'],
            seat_type=data['seat_type'],
            is_available=True
        )
        
        db.session.add(seat)
        db.session.commit()
        
        return jsonify({
            'message': 'Seat created successfully',
            'seat': seat.to_dict()
        }), 201
        
    except ValueError as ve:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@seat_bp.route('/bulk', methods=['POST'])
@admin_required
def create_bulk_seats():
    """Create multiple seats at once (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'schedule_id' not in data or 'journey_date' not in data or 'seats' not in data:
            return jsonify({'error': 'schedule_id, journey_date, and seats array required'}), 400
        
        schedule = Schedule.query.get(data['schedule_id'])
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        journey_date = datetime.strptime(data['journey_date'], '%Y-%m-%d').date()
        
        created_seats = []
        for seat_info in data['seats']:
            # Check if seat already exists
            existing = Seat.query.filter_by(
                schedule_id=data['schedule_id'],
                journey_date=journey_date,
                seat_number=seat_info['seat_number']
            ).first()
            
            if not existing:
                seat = Seat(
                    schedule_id=data['schedule_id'],
                    journey_date=journey_date,
                    seat_number=seat_info['seat_number'],
                    seat_type=seat_info['seat_type'],
                    is_available=True
                )
                db.session.add(seat)
                created_seats.append(seat)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_seats)} seats created successfully',
            'seats': [seat.to_dict() for seat in created_seats]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@seat_bp.route('/<int:seat_id>', methods=['PUT'])
@admin_required
def update_seat(seat_id):
    """Update seat availability (admin only)"""
    try:
        seat = Seat.query.get(seat_id)
        if not seat:
            return jsonify({'error': 'Seat not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'is_available' in data:
            seat.is_available = data['is_available']
        if 'seat_type' in data:
            seat.seat_type = data['seat_type']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Seat updated successfully',
            'seat': seat.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@seat_bp.route('/<int:seat_id>', methods=['DELETE'])
@admin_required
def delete_seat(seat_id):
    """Delete seat (admin only)"""
    try:
        seat = Seat.query.get(seat_id)
        if not seat:
            return jsonify({'error': 'Seat not found'}), 404
        
        db.session.delete(seat)
        db.session.commit()
        
        return jsonify({
            'message': 'Seat deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
