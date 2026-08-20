"""
app.py
------
Main Flask application for Smart Complaint Prioritization Using AI.
Handles all routes for users, admin, and REST API endpoints.
"""

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

from database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    get_all_users, create_complaint, get_complaint_by_id,
    get_complaints_by_user, get_all_complaints,
    update_complaint_status, delete_complaint, get_stats
)
from model import predict_priority

# ================================================================== #
#  APP CONFIGURATION
# ================================================================== #

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smartcomplaint_secret_2024_xyz')

# Available complaint categories
CATEGORIES = [
    "Safety", "Electricity", "Water", "Roads",
    "Sanitation", "Security", "Environment", "Health", "General"
]

# Valid status transitions
VALID_STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]

# ================================================================== #
#  DECORATORS
# ================================================================== #

def login_required(f):
    """Redirect to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Restrict route to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ================================================================== #
#  PUBLIC ROUTES
# ================================================================== #

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if len(name) < 2:
            flash('Name must be at least 2 characters.', 'danger')
            return render_template('register.html')

        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        # Check if email already exists
        if get_user_by_email(email):
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        # Create user
        hashed = generate_password_hash(password)
        user_id = create_user(name, email, hashed)

        session['user_id'] = user_id
        session['user_name'] = name
        session['role'] = 'user'
        flash(f'Welcome, {name}! Your account has been created.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User and admin login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard') if session.get('role') == 'user' else url_for('admin_dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        user = get_user_by_email(email)

        if not user or not check_password_hash(user['password'], password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        # Set session
        session['user_id']   = user['id']
        session['user_name'] = user['name']
        session['role']      = user['role']

        flash(f'Welcome back, {user["name"]}!', 'success')

        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear session and redirect to landing page."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ================================================================== #
#  USER ROUTES
# ================================================================== #

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with complaint summary."""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    user = get_user_by_id(session['user_id'])
    complaints = get_complaints_by_user(session['user_id'])

    # Stats for the user
    stats = {
        'total':     len(complaints),
        'pending':   sum(1 for c in complaints if c['status'] == 'Pending'),
        'resolved':  sum(1 for c in complaints if c['status'] == 'Resolved'),
        'critical':  sum(1 for c in complaints if c['priority'] == 'Critical'),
    }

    # Recent 5 complaints
    recent = list(complaints)[:5]
    return render_template('user_dashboard.html', user=user, stats=stats, recent=recent)


@app.route('/complaint/new', methods=['GET', 'POST'])
@login_required
def complaint_new():
    """Submit a new complaint."""
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category    = request.form.get('category', '').strip()

        # Validation
        if not title or not description or not category:
            flash('All fields are required.', 'danger')
            return render_template('complaint_new.html', categories=CATEGORIES)

        if len(title) < 5:
            flash('Title must be at least 5 characters.', 'danger')
            return render_template('complaint_new.html', categories=CATEGORIES)

        if len(description) < 20:
            flash('Please provide a more detailed description (min 20 characters).', 'danger')
            return render_template('complaint_new.html', categories=CATEGORIES)

        if category not in CATEGORIES:
            flash('Invalid category selected.', 'danger')
            return render_template('complaint_new.html', categories=CATEGORIES)

        # AI prioritization
        result = predict_priority(title, description)

        # Save to database
        complaint_id = create_complaint(
            user_id        = session['user_id'],
            title          = title,
            description    = description,
            category       = result['category'] if result['category'] != 'General' else category,
            priority       = result['priority'],
            priority_score = result['score']
        )

        flash(
            f'Complaint submitted! AI assigned priority: <strong>{result["priority"]}</strong> '
            f'(Score: {result["score"]}/100)',
            'success'
        )
        return redirect(url_for('complaint_details', complaint_id=complaint_id))

    return render_template('complaint_new.html', categories=CATEGORIES)


@app.route('/complaints')
@login_required
def my_complaints():
    """List all complaints submitted by the logged-in user."""
    status   = request.args.get('status', '')
    priority = request.args.get('priority', '')

    complaints = get_complaints_by_user(session['user_id'])

    # Client-side filter (small dataset, fine to filter in Python)
    if status:
        complaints = [c for c in complaints if c['status'] == status]
    if priority:
        complaints = [c for c in complaints if c['priority'] == priority]

    return render_template(
        'my_complaints.html',
        complaints=complaints,
        selected_status=status,
        selected_priority=priority,
        statuses=VALID_STATUSES
    )


@app.route('/complaint/<int:complaint_id>')
@login_required
def complaint_details(complaint_id):
    """View details of a specific complaint."""
    complaint = get_complaint_by_id(complaint_id)

    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('my_complaints'))

    # Only allow if owner or admin
    if complaint['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('my_complaints'))

    return render_template('complaint_details.html', complaint=complaint)


# ================================================================== #
#  ADMIN ROUTES
# ================================================================== #

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with analytics."""
    stats = get_stats()
    return render_template('admin_dashboard.html', stats=stats)


@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    """Admin view of all complaints with search and filters."""
    search   = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    status   = request.args.get('status', '')
    priority = request.args.get('priority', '')

    complaints = get_all_complaints(
        category = category or None,
        status   = status or None,
        priority = priority or None,
        search   = search or None,
    )

    return render_template(
        'admin_complaints.html',
        complaints  = complaints,
        categories  = CATEGORIES,
        statuses    = VALID_STATUSES,
        priorities  = ['Low', 'Medium', 'High', 'Critical'],
        search      = search,
        sel_cat     = category,
        sel_status  = status,
        sel_priority= priority,
    )


@app.route('/admin/complaint/<int:complaint_id>')
@admin_required
def admin_complaint_details(complaint_id):
    """Admin detailed view of a complaint (reuses complaint_details template)."""
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin_complaints'))

    return render_template('complaint_details.html', complaint=complaint, is_admin=True, statuses=VALID_STATUSES)


@app.route('/admin/update-status/<int:complaint_id>', methods=['POST'])
@admin_required
def admin_update_status(complaint_id):
    """Update complaint status via form POST."""
    new_status = request.form.get('status', '')
    if new_status not in VALID_STATUSES:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('admin_complaint_details', complaint_id=complaint_id))

    update_complaint_status(complaint_id, new_status)
    flash(f'Complaint status updated to <strong>{new_status}</strong>.', 'success')
    return redirect(url_for('admin_complaint_details', complaint_id=complaint_id))


@app.route('/admin/delete/<int:complaint_id>', methods=['POST'])
@admin_required
def admin_delete_complaint(complaint_id):
    """Delete a complaint permanently."""
    delete_complaint(complaint_id)
    flash('Complaint deleted successfully.', 'info')
    return redirect(url_for('admin_complaints'))


@app.route('/admin/users')
@admin_required
def admin_users():
    """List all registered users."""
    users = get_all_users()
    return render_template('admin_users.html', users=users)


# ================================================================== #
#  REST API ENDPOINTS
# ================================================================== #

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """
    Live AI analysis endpoint called from the complaint form.
    Expects JSON: {"title": "...", "description": "..."}
    Returns JSON: {"priority": "...", "score": ..., "category": "..."}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    title       = str(data.get('title', '')).strip()
    description = str(data.get('description', '')).strip()

    if not title or not description:
        return jsonify({'error': 'Title and description required'}), 400

    result = predict_priority(title, description)
    return jsonify(result)


@app.route('/api/stats')
@admin_required
def api_stats():
    """Return analytics stats as JSON for Chart.js."""
    return jsonify(get_stats())


# ================================================================== #
#  ERROR HANDLERS
# ================================================================== #

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


# ================================================================== #
#  STARTUP
# ================================================================== #

if __name__ == '__main__':
    # Initialize database tables
    init_db()
    print("\n✅  Database initialized successfully.")

    # Create default admin account if it doesn't exist
    admin_email = 'admin@smartcomplaint.com'
    if not get_user_by_email(admin_email):
        from werkzeug.security import generate_password_hash as gph
        create_user(
            name            = 'Administrator',
            email           = admin_email,
            hashed_password = gph('Admin@1234'),
            role            = 'admin'
        )
        print("✅  Default admin account created.")
        print("    Email    : admin@smartcomplaint.com")
        print("    Password : Admin@1234\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
