# Train Booking System - Setup Checklist

Follow these steps to set up the complete train booking system.

## ✅ Pre-Setup Checklist

- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Git installed (optional)
- [ ] Text editor or IDE (VS Code, PyCharm, etc.)

## 📁��� Step 1: Create Project Structure

```bash
# Create main project directory
mkdir train-booking-system
cd train-booking-system

# Create subdirectories
mkdir routes
mkdir templates

# Create __init__.py for routes module
touch routes/__init__.py
```

## 📝��� Step 2: Create Backend Files

Create these files in the root directory:

### Core Application Files
- [ ] `app.py` - Main Flask application
- [ ] `config.py` - Configuration settings
- [ ] `models.py` - SQLAlchemy database models
- [ ] `requirements.txt` - Python dependencies
- [ ] `seed_data.py` - Database seeding script

### Route Files (in `routes/` directory)
- [ ] `routes/__init__.py` - Empty init file
- [ ] `routes/auth_routes.py` - Authentication endpoints
- [ ] `routes/user_routes.py` - User management
- [ ] `routes/train_routes.py` - Train management
- [ ] `routes/route_routes.py` - Route management
- [ ] `routes/schedule_routes.py` - Schedule management
- [ ] `routes/ticket_routes.py` - Ticket booking
- [ ] `routes/seat_routes.py` - Seat management
- [ ] `routes/payment_routes.py` - Payment processing
- [ ] `routes/web_routes.py` - Frontend routes

## 🎨��� Step 3: Create Frontend Templates

Create these files in the `templates/` directory:

- [ ] `templates/base.html` - Base template with navbar
- [ ] `templates/index.html` - Home page
- [ ] `templates/login.html` - Login page
- [ ] `templates/register.html` - Registration page
- [ ] `templates/search.html` - Search trains
- [ ] `templates/book.html` - Book tickets
- [ ] `templates/tickets.html` - View tickets
- [ ] `templates/admin_trains.html` - Admin train management

## 🐳��� Step 4: Create Docker Files

Create these files in the root directory:

- [ ] `Dockerfile` - Flask application container
- [ ] `docker-compose.yml` - Multi-container orchestration
- [ ] `init.sql` - Database initialization script
- [ ] `.dockerignore` - Files to exclude from Docker build
- [ ] `.env.example` - Example environment variables

## 🔧��� Step 5: Verify File Structure

Your project should look like this:

```
train-booking-system/
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── user_routes.py
│   ├── train_routes.py
│   ├── route_routes.py
│   ├── schedule_routes.py
│   ├── ticket_routes.py
│   ├── seat_routes.py
│   ├── payment_routes.py
│   └── web_routes.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── search.html
│   ├── book.html
│   ├── tickets.html
│   └── admin_trains.html
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── seed_data.py
├── Dockerfile
├── docker-compose.yml
├── init.sql
└── .env.example
```

## 🚀��� Step 6: Build and Run

```bash
# Build Docker containers
docker-compose build

# Start services in detached mode
docker-compose up -d

# Check if containers are running
docker ps

# Expected output:
# CONTAINER ID   IMAGE                    NAMES
# xxxxxxxxx      train-booking-system     train_booking_app
# yyyyyyyyy      mysql:8.0               train_booking_mysql
```

## ⏳ Step 7: Wait for Services

```bash
# Watch the logs to see when services are ready
docker-compose logs -f

# Wait for messages like:
# - "MySQL init process done. Ready for start up."
# - "Database tables created successfully!"
# - "Running on http://0.0.0.0:5000"

# Press Ctrl+C to stop watching logs
```

## 🌱��� Step 8: Seed the Database

```bash
# Run the seed script to populate sample data
docker exec -it train_booking_app python seed_data.py

# Expected output:
# ✅ Database seeded successfully!
# 📝��� Sample Login Credentials:
# Admin: username='admin', password='admin123'
# User 1: username='john_doe', password='password123'
# User 2: username='jane_smith', password='password123'
```

## 🧪��� Step 9: Test the Application

### Test 1: Access the Home Page
- [ ] Open browser: `http://localhost:5000`
- [ ] Verify home page loads
- [ ] Check navbar links work

### Test 2: User Registration
- [ ] Go to `/register`
- [ ] Fill form with test data
- [ ] Click "Register"
- [ ] Verify success message

### Test 3: User Login
- [ ] Go to `/login`
- [ ] Login with: `username: john_doe, password: password123`
- [ ] Verify redirect to dashboard
- [ ] Check navbar shows logout button

### Test 4: Search Trains
- [ ] Go to `/search`
- [ ] Enter: Source="New Delhi", Destination="Mumbai"
- [ ] Click "Search Trains"
- [ ] Verify results appear

### Test 5: Book a Ticket
- [ ] From search results, click "Book Now"
- [ ] Fill passenger details
- [ ] Select future date
- [ ] Click "Book Ticket"
- [ ] Verify success message with PNR

### Test 6: View Tickets
- [ ] Go to `/tickets`
- [ ] Verify your booking appears
- [ ] Check PNR, status, and details

### Test 7: PNR Status Check
- [ ] Go to home page
- [ ] Enter the PNR from your booking
- [ ] Click "Check Status"
- [ ] Verify ticket details display

### Test 8: Admin Login
- [ ] Logout if logged in
- [ ] Login with: `username: admin, password: admin123`
- [ ] Verify "Admin" link in navbar

### Test 9: Admin Functions
- [ ] Go to `/admin/trains`
- [ ] Try adding a new train
- [ ] Try deleting a train
- [ ] Verify operations work

### Test 10: API Endpoints
```bash
# Test API directly with curl

# Get all trains
curl http://localhost:5000/api/trains/

# Login and get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"password123"}'

# Use token for protected endpoints
curl http://localhost:5000/api/tickets/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐛��� Step 10: Troubleshooting

If something doesn't work:

### Container Issues
```bash
# Check container status
docker ps -a

# View logs
docker-compose logs flask_app
docker-compose logs mysql

# Restart services
docker-compose restart

# Complete rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues
```bash
# Access MySQL
docker exec -it train_booking_mysql mysql -u trainuser -ptrainpass train_booking_db

# Check tables
SHOW TABLES;

# Check data
SELECT * FROM users;
```

### Application Issues
```bash
# Access Flask container
docker exec -it train_booking_app /bin/bash

# Check Python version
python --version

# Check if app file exists
ls -la

# Run seed script manually
python seed_data.py
```

## ✨ Step 11: Verify Complete Setup

All these should work:

- [ ] Home page loads at `http://localhost:5000`
- [ ] User can register new account
- [ ] User can login successfully
- [ ] User can search trains
- [ ] User can book tickets
- [ ] User can view their tickets
- [ ] User can cancel tickets
- [ ] PNR status check works
- [ ] Admin can login
- [ ] Admin can manage trains
- [ ] All API endpoints respond correctly
- [ ] No errors in Docker logs

## 🎉��� Success!

If all checkboxes are ticked, your train booking system is fully set up and running!

## 📞��� Next Steps

1. Explore the admin panel
2. Book multiple tickets
3. Test different scenarios
4. Read the main README.md for API documentation
5. Customize the application as needed

## 💡��� Tips

- Keep Docker containers running while testing
- Check logs regularly: `docker-compose logs -f`
- Use `docker-compose down` when done to stop services
- Backup your data before major changes
- Read error messages carefully

## 🔄��� Daily Development Workflow

```bash
# Start your day
docker-compose up -d

# View logs while developing
docker-compose logs -f flask_app

# Make code changes (they'll auto-reload in development)

# Restart if needed
docker-compose restart flask_app

# End your day
docker-compose down
```

---

**Happy Codding!
