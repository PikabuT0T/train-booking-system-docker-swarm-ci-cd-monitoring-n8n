-- Initialize the database with sample data

USE train_booking_db;

-- This file is executed automatically when the MySQL container starts for the first time
-- The tables will be created by SQLAlchemy when the Flask app starts

-- Note: We don't create tables here as SQLAlchemy will handle that
-- This file can be used for additional initialization if needed

SELECT 'Database initialized successfully' as message;
