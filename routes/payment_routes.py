"""
Payment Management Routes - CRUD operations for payments
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Payment, Ticket
import random
import string

payment_bp = Blueprint('payments', __name__)


def generate_transaction_id():
    """Generate unique transaction ID"""
    return 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))


@payment_bp.route('/', methods=['POST'])
@jwt_required()
def create_payment():
    """Process a payment for a ticket"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['ticket_id', 'amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify ticket exists and belongs to user
        ticket = Ticket.query.get(data['ticket_id'])
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        if ticket.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if payment already exists for this ticket
        existing_payment = Payment.query.filter_by(
            ticket_id=data['ticket_id'],
            payment_status='completed'
        ).first()
        
        if existing_payment:
            return jsonify({'error': 'Payment already completed for this ticket'}), 400
        
        # Generate unique transaction ID
        transaction_id = generate_transaction_id()
        while Payment.query.filter_by(transaction_id=transaction_id).first():
            transaction_id = generate_transaction_id()
        
        # Create payment record
        payment = Payment(
            ticket_id=data['ticket_id'],
            user_id=current_user_id,
            amount=data['amount'],
            payment_method=data['payment_method'],
            payment_status='completed',  # Simulate successful payment
            transaction_id=transaction_id
        )
        
        db.session.add(payment)
        
        # Update ticket status to confirmed
        if ticket.status == 'pending':
            ticket.status = 'confirmed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment processed successfully',
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    """Get all payments for logged-in user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Admin can see all payments, users see only their own
        if current_user.role == 'admin':
            payments = Payment.query.all()
        else:
            payments = Payment.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments],
            'count': len(payments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment by ID"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Users can only view their own payments unless admin
        if current_user.role != 'admin' and payment.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/transaction/<string:transaction_id>', methods=['GET'])
@jwt_required()
def get_payment_by_transaction(transaction_id):
    """Get payment by transaction ID"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Users can only view their own payments unless admin
        if current_user.role != 'admin' and payment.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    """Delete payment record (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        db.session.delete(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/<int:payment_id>/refund', methods=['PUT'])
@jwt_required()
def refund_payment(payment_id):
    """Refund a payment (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.payment_status == 'refunded':
            return jsonify({'error': 'Payment already refunded'}), 400
        
        payment.payment_status = 'refunded'
        
        # Update associated ticket
        ticket = Ticket.query.get(payment.ticket_id)
        if ticket:
            ticket.status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment refunded successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
