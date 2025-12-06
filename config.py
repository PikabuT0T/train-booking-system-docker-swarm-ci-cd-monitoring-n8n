"""
Configuration settings for Flask application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'trainuser')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'trainpass')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'train_booking_db')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
