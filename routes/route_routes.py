"""
Route Management Routes - CRUD operations for routes
"""
from flask import Blueprint, request, jsonify, session
from models import db, User, Route
from routes.auth_helpers import login_required, admin_required

route_bp = Blueprint('routes', __name__)


@route_bp.route('/', methods=['GET'])
def get_all_routes():
    """Get all routes - public access"""
    try:
        # Optional filters
        status = request.args.get('status')
        source = request.args.get('source')
        destination = request.args.get('destination')
        
        query = Route.query
        
        if status:
            query = query.filter_by(status=status)
        if source:
            query = query.filter(Route.source_station.like(f'%{source}%'))
        if destination:
            query = query.filter(Route.destination_station.like(f'%{destination}%'))
        
        routes = query.all()
        
        return jsonify({
            'routes': [route.to_dict() for route in routes],
            'count': len(routes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@route_bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    """Get route by ID - public access"""
    try:
        route = Route.query.get(route_id)
        
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        return jsonify({
            'route': route.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@route_bp.route('/', methods=['POST'])
@admin_required
def create_route():
    """Create new route - admin only"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['route_name', 'source_station', 'destination_station', 
                          'distance_km', 'duration_hours']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new route
        route = Route(
            route_name=data['route_name'],
            source_station=data['source_station'],
            destination_station=data['destination_station'],
            distance_km=data['distance_km'],
            duration_hours=data['duration_hours'],
            status=data.get('status', 'active')
        )
        
        db.session.add(route)
        db.session.commit()
        
        return jsonify({
            'message': 'Route created successfully',
            'route': route.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@route_bp.route('/<int:route_id>', methods=['PUT'])
@admin_required
def update_route(route_id):
    """Update route information - admin only"""
    try:
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'route_name' in data:
            route.route_name = data['route_name']
        if 'source_station' in data:
            route.source_station = data['source_station']
        if 'destination_station' in data:
            route.destination_station = data['destination_station']
        if 'distance_km' in data:
            route.distance_km = data['distance_km']
        if 'duration_hours' in data:
            route.duration_hours = data['duration_hours']
        if 'status' in data:
            route.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Route updated successfully',
            'route': route.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@route_bp.route('/<int:route_id>', methods=['DELETE'])
@admin_required
def delete_route(route_id):
    """Delete route - admin only"""
    try:
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        db.session.delete(route)
        db.session.commit()
        
        return jsonify({
            'message': 'Route deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
