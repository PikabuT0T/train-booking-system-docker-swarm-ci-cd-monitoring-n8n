"""
Web Routes - Frontend page rendering
"""
from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def home():
    """Home page"""
    return render_template('index.html')


@web_bp.route('/register')
def register_page():
    """Registration page"""
    return render_template('register.html')


@web_bp.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


@web_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')


@web_bp.route('/trains')
def trains_page():
    """Trains listing page"""
    return render_template('trains.html')


@web_bp.route('/search')
def search_page():
    """Search trains page"""
    return render_template('search.html')


@web_bp.route('/book/<int:schedule_id>')
def book_page(schedule_id):
    """Booking page"""
    return render_template('book.html', schedule_id=schedule_id)


@web_bp.route('/tickets')
def tickets_page():
    """My tickets page"""
    return render_template('tickets.html')


@web_bp.route('/admin')
def admin_page():
    """Admin dashboard"""
    return render_template('admin.html')


@web_bp.route('/admin/trains')
def admin_trains():
    """Admin trains management"""
    return render_template('admin_trains.html')


@web_bp.route('/admin/routes')
def admin_routes():
    """Admin routes management"""
    return render_template('admin_routes.html')


@web_bp.route('/admin/schedules')
def admin_schedules():
    """Admin schedules management"""
    return render_template('admin_schedules.html')
