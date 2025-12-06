"""
Ticket Booking Routes - CRUD operations for tickets
"""
from flask import Blueprint, request, jsonify, session
from models import db, User, Ticket, Schedule, Seat
from routes.auth_helpers import login_required, get_current_user_id
from datetime import datetime, date
import random
import string

ticket_bp = Blueprint('tickets', __name__)


def generate_pnr():
    """Generate unique PNR number"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@ticket_bp.route('/', methods=['POST'])
@login_required
def book_ticket():
    """Book a new ticket"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['schedule_id', 'journey_date', 'passenger_name', 
                          'passenger_age', 'passenger_gender']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify schedule exists
        schedule = Schedule.query.get(data['schedule_id'])
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        if schedule.status != 'active':
            return jsonify({'error': 'Schedule is not active'}), 400
        
        # Parse journey date
        journey_date = datetime.strptime(data['journey_date'], '%Y-%m-%d').date()
        
        # Check if journey date is in the future
        if journey_date < date.today():
            return jsonify({'error': 'Journey date must be in the future'}), 400
        
        # Check available seats
        available_seats = Seat.query.filter_by(
            schedule_id=data['schedule_id'],
            journey_date=journey_date,
            is_available=True
        ).first()
        
        # Generate unique PNR
        pnr = generate_pnr()
        while Ticket.query.filter_by(pnr_number=pnr).first():
            pnr = generate_pnr()
        
        # Create ticket
        ticket = Ticket(
            user_id=current_user_id,
            schedule_id=data['schedule_id'],
            booking_date=date.today(),
            journey_date=journey_date,
            passenger_name=data['passenger_name'],
            passenger_age=data['passenger_age'],
            passenger_gender=data['passenger_gender'],
            fare=schedule.base_fare,
            pnr_number=pnr,
            status='pending' if not available_seats else 'confirmed',
            seat_number=available_seats.seat_number if available_seats else None
        )
        
        db.session.add(ticket)
        
        # Reserve seat if available
        if available_seats:
            available_seats.is_available = False
            available_seats.ticket_id = ticket.id
            ticket.seat_number = available_seats.seat_number
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket booked successfully',
            'ticket': ticket.to_dict()
        }), 201
        
    except ValueError as ve:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/', methods=['GET'])
@login_required
def get_user_tickets():
    """Get all tickets for logged-in user"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        # Admin can see all tickets, users see only their own
        if current_user.role == 'admin':
            tickets = Ticket.query.all()
        else:
            tickets = Ticket.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'tickets': [ticket.to_dict() for ticket in tickets],
            'count': len(tickets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    """Get ticket by ID"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Users can only view their own tickets unless admin
        if current_user.role != 'admin' and ticket.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'ticket': ticket.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/pnr/<string:pnr>', methods=['GET'])
def get_ticket_by_pnr(pnr):
    """Get ticket by PNR number (public access)"""
    try:
        ticket = Ticket.query.filter_by(pnr_number=pnr).first()
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Get schedule details
        schedule = Schedule.query.get(ticket.schedule_id)
        ticket_dict = ticket.to_dict()
        ticket_dict['schedule'] = schedule.to_dict() if schedule else None
        
        return jsonify({
            'ticket': ticket_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<int:ticket_id>/cancel', methods=['PUT'])
@login_required
def cancel_ticket(ticket_id):
    """Cancel a ticket"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Users can only cancel their own tickets unless admin
        if current_user.role != 'admin' and ticket.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if ticket.status == 'cancelled':
            return jsonify({'error': 'Ticket already cancelled'}), 400
        
        # Cancel ticket
        ticket.status = 'cancelled'
        
        # Release seat if reserved
        if ticket.seat_number:
            seat = Seat.query.filter_by(
                schedule_id=ticket.schedule_id,
                journey_date=ticket.journey_date,
                seat_number=ticket.seat_number
            ).first()
            
            if seat:
                seat.is_available = True
                seat.ticket_id = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket cancelled successfully',
            'ticket': ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    """Delete ticket (admin only)"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        db.session.delete(ticket)
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
