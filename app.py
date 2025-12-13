"""
Main Flask Application for Train Booking System
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
#from flask_jwt_extended import JWTManager
from models import db
from config import Config

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Authorization"],
     supports_credentials=True)
#    jwt = JWTManager(app)
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.train_routes import train_bp
    from routes.route_routes import route_bp
    from routes.schedule_routes import schedule_bp
    from routes.ticket_routes import ticket_bp
    from routes.seat_routes import seat_bp
#    from routes.payment_routes import payment_bp
    from routes.web_routes import web_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(train_bp, url_prefix='/api/trains')
    app.register_blueprint(route_bp, url_prefix='/api/routes')
    app.register_blueprint(schedule_bp, url_prefix='/api/schedules')
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets')
    app.register_blueprint(seat_bp, url_prefix='/api/seats')
#    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(web_bp)  # Frontend routes
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
#    @jwt.unauthorized_loader
#    def unauthorized_callback(callback):
#        return jsonify({'error': 'Missing or invalid token'}), 401
    
#    @jwt.invalid_token_loader
#    def invalid_token_callback(callback):
#        return jsonify({'error': 'Invalid token'}), 401
    
#    @jwt.expired_token_loader
#    def expired_token_callback(jwt_header, jwt_payload):
#        return jsonify({'error': 'Token has expired'}), 401
    
    # Database initialization
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
    
        if not existing_tables:
            db.create_all()
            print("Database tables created successfully!")
        else:
            print(f"Database ready ({len(existing_tables)} tables exist)")

    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Train Booking System API',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'trains': '/api/trains',
                'routes': '/api/routes',
                'schedules': '/api/schedules',
                'tickets': '/api/tickets',
                'seats': '/api/seats',
#                'payments': '/api/payments',
                'web': '/'
            }
        })
    
    return app


app = create_app()

if __name__ == '__main__':
#    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)



