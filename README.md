# 🚂��� Train Booking System

A comprehensive full-stack train booking system built with Python Flask, MySQL, and Docker.

## 📋��� Features

### User Features
- User registration and authentication (JWT-based)
- Search trains by source and destination
- View train schedules and availability
- Book tickets with passenger details
- View booking history
- Cancel tickets
- Check PNR status

### Admin Features
- Manage trains (CRUD operations)
- Manage routes (CRUD operations)
- Manage schedules (CRUD operations)
- Manage seats availability
- View all bookings and payments
- User management

## 🏗���️ Architecture

### Backend
- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Database**: MySQL 8.0
- **API**: RESTful API with 41 endpoints

### Frontend
- **Template Engine**: Jinja2
- **Styling**: Custom CSS
- **JavaScript**: Vanilla JS with Fetch API

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: MySQL in Docker container
- **Application**: Flask in Docker container

## 📁��� Project Structure

```
train-booking-system/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── models.py                   # SQLAlchemy models
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration for Flask app
├── docker-compose.yml          # Docker Compose configuration
├── init.sql                    # Database initialization script
├── seed_data.py               # Sample data seeding script
├── routes/
│   ├── auth_routes.py         # Authentication endpoints
│   ├── user_routes.py         # User management endpoints
│   ├── train_routes.py        # Train management endpoints
│   ├── route_routes.py        # Route management endpoints
│   ├── schedule_routes.py     # Schedule management endpoints
│   ├── ticket_routes.py       # Ticket booking endpoints
│   ├── seat_routes.py         # Seat management endpoints
│   ├── payment_routes.py      # Payment endpoints
│   └── web_routes.py          # Frontend page routes
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Home page
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── search.html            # Search trains page
    ├── book.html              # Booking page
    ├── tickets.html           # User tickets page
    └── admin_trains.html      # Admin train management
```

## 🚀��� Getting Started

### Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Installation Steps

1. **Clone or create the project directory**
```bash
mkdir train-booking-system
cd train-booking-system
```

2. **Create the required files**

Create all the files as shown in the project structure above with the provided code.

3. **Create the routes directory**
```bash
mkdir routes
touch routes/__init__.py
```

4. **Create the templates directory**
```bash
mkdir templates
```

5. **Build and run with Docker**
```bash
# Build the containers
docker-compose build

# Start the services
docker-compose up -d

# Check if containers are running
docker ps
```

6. **Wait for services to start** (about 30 seconds)

7. **Seed the database with sample data**
```bash
docker exec -it train_booking_app python seed_data.py
```

8. **Access the application**
- Open your browser and navigate to: `http://localhost:5000`

## 🔑��� Default Credentials

After running the seed script, you can login with:

### Admin Account
- Username: `admin`
- Password: `admin123`

### User Accounts
- Username: `john_doe` | Password: `password123`
- Username: `jane_smith` | Password: `password123`

## 📡��� API Endpoints

### Authentication (3 endpoints)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Users (4 endpoints)
- `GET /api/users/` - Get all users (admin)
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

### Trains (6 endpoints)
- `GET /api/trains/` - Get all trains
- `GET /api/trains/<id>` - Get train by ID
- `POST /api/trains/` - Create train (admin)
- `PUT /api/trains/<id>` - Update train (admin)
- `DELETE /api/trains/<id>` - Delete train (admin)
- `GET /api/trains/search?q=query` - Search trains

### Routes (5 endpoints)
- `GET /api/routes/` - Get all routes
- `GET /api/routes/<id>` - Get route by ID
- `POST /api/routes/` - Create route (admin)
- `PUT /api/routes/<id>` - Update route (admin)
- `DELETE /api/routes/<id>` - Delete route (admin)

### Schedules (6 endpoints)
- `GET /api/schedules/` - Get all schedules
- `GET /api/schedules/<id>` - Get schedule by ID
- `POST /api/schedules/` - Create schedule (admin)
- `PUT /api/schedules/<id>` - Update schedule (admin)
- `DELETE /api/schedules/<id>` - Delete schedule (admin)
- `GET /api/schedules/search?source=X&destination=Y` - Search schedules

### Tickets (6 endpoints)
- `POST /api/tickets/` - Book ticket
- `GET /api/tickets/` - Get user tickets
- `GET /api/tickets/<id>` - Get ticket by ID
- `GET /api/tickets/pnr/<pnr>` - Get ticket by PNR
- `PUT /api/tickets/<id>/cancel` - Cancel ticket
- `DELETE /api/tickets/<id>` - Delete ticket (admin)

### Seats (5 endpoints)
- `GET /api/seats/?schedule_id=X&journey_date=Y` - Get available seats
- `POST /api/seats/` - Create seat (admin)
- `POST /api/seats/bulk` - Create multiple seats (admin)
- `PUT /api/seats/<id>` - Update seat (admin)
- `DELETE /api/seats/<id>` - Delete seat (admin)

### Payments (6 endpoints)
- `POST /api/payments/` - Process payment
- `GET /api/payments/` - Get user payments
- `GET /api/payments/<id>` - Get payment by ID
- `GET /api/payments/transaction/<txn_id>` - Get by transaction ID
- `DELETE /api/payments/<id>` - Delete payment (admin)
- `PUT /api/payments/<id>/refund` - Refund payment (admin)

**Total: 41 API endpoints**

## 🧪��� Testing the Application

### Testing User Flow

1. **Register a new account**
   - Go to `/register`
   - Fill in the registration form
   - Click "Register"

2. **Login**
   - Go to `/login`
   - Use your credentials
   - You'll be redirected to the dashboard

3. **Search for trains**
   - Go to `/search`
   - Enter source and destination
   - Click "Search Trains"

4. **Book a ticket**
   - Click "Book Now" on any train
   - Fill in passenger details
   - Select journey date
   - Click "Book Ticket"

5. **View your tickets**
   - Go to `/tickets`
   - See all your bookings
   - Cancel if needed

6. **Check PNR status**
   - Go to home page
   - Enter PNR number
   - View ticket details

### Testing Admin Flow

1. **Login as admin**
   - Username: `admin`
   - Password: `admin123`

2. **Manage trains**
   - Go to `/admin/trains`
   - Add, edit, or delete trains

3. **View all bookings**
   - Access admin dashboard
   - View system-wide statistics

## 🐛��� Troubleshooting

### Container Issues

```bash
# View container logs
docker-compose logs flask_app
docker-compose logs mysql

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Check MySQL is ready
docker exec -it train_booking_mysql mysql -u trainuser -ptrainpass -e "SHOW DATABASES;"

# Access MySQL shell
docker exec -it train_booking_mysql mysql -u trainuser -ptrainpass train_booking_db
```

### Application Issues

```bash
# Access Flask container shell
docker exec -it train_booking_app /bin/bash

# Run seed script again
docker exec -it train_booking_app python seed_data.py
```

## 🛠���️ Development

### Running without Docker

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up MySQL locally**
```bash
mysql -u root -p
CREATE DATABASE train_booking_db;
CREATE USER 'trainuser'@'localhost' IDENTIFIED BY 'trainpass';
GRANT ALL PRIVILEGES ON train_booking_db.* TO 'trainuser'@'localhost';
FLUSH PRIVILEGES;
```

3. **Update config.py**
```python
MYSQL_HOST = 'localhost'
```

4. **Run the application**
```bash
python app.py
```

5. **Seed the database**
```bash
python seed_data.py
```

## 📊��� Database Schema

The system uses 7 main tables:

1. **users** - User accounts and authentication
2. **trains** - Train information
3. **routes** - Route details (source, destination, distance)
4. **schedules** - Train schedules (links trains to routes)
5. **tickets** - Booking records
6. **seats** - Seat availability management
7. **payments** - Payment transactions

## 🔒��� Security Features

- Password hashing using Werkzeug
- JWT-based authentication
- Role-based access control (User/Admin)
- Protected API endpoints
- SQL injection prevention (SQLAlchemy ORM)
- CORS enabled

## 📈��� Future Enhancements

- Payment gateway integration
- Email notifications
- SMS alerts
- Real-time seat availability
- Train tracking
- Multiple passenger booking
- Waitlist management
- Rating and reviews
- Mobile app
- Analytics dashboard

## 🤝��� Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄��� License

This project is open source and available under the MIT License.

## 👥��� Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## 🙏��� Acknowledgments

- Flask framework
- SQLAlchemy ORM
- MySQL database
- Docker containerization

---

**Built with ❤️ for learning and demonstration purposes
# CI/CD test Sun Dec  7 12:12:04 AM EET 2025
