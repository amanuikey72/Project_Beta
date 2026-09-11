"""
database.py
-----------
SQLite database initialization and helper functions.
Handles all DB operations for the Smart Complaint Prioritization system.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'complaints.db')


def get_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows column access by name
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
    return conn


def init_db():
    """Initialize database tables and indexes if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ------------------------------------------------------------------ #
    #  USERS TABLE
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'user',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ------------------------------------------------------------------ #
    #  COMPLAINTS TABLE
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            title          TEXT    NOT NULL,
            description    TEXT    NOT NULL,
            category       TEXT    NOT NULL,
            priority       TEXT    NOT NULL DEFAULT 'Low',
            priority_score INTEGER NOT NULL DEFAULT 0,
            status         TEXT    NOT NULL DEFAULT 'Pending',
            created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at     TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create Indexes for high performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_user ON complaints(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_score ON complaints(priority_score DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category)")

    conn.commit()
    conn.close()
    seed_sample_data()


def seed_sample_data():
    """Seed initial sample users and complaints if database is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]

    if count == 0:
        from werkzeug.security import generate_password_hash
        # Create a sample citizen user if not exists
        cursor.execute("SELECT id FROM users WHERE email = 'user@example.com'")
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ('Rahul Sharma', 'user@example.com', generate_password_hash('User@1234'), 'user')
            )
            user_id = cursor.lastrowid
        else:
            user_id = user_row['id']

        samples = [
            ("Gas Leakage in Residential Complex", "There is a severe gas leakage near Building B. Strong smell of LPG and people are facing breathing difficulty. Please send emergency team immediately!", "Safety", "Critical", 98, "Pending"),
            ("Major High Voltage Wire Fallen on Main Road", "A high voltage electric wire has snapped and fallen near the public school entrance. Severe danger of electrocution for kids and commuters.", "Electricity", "Critical", 92, "In Progress"),
            ("Drinking Water Pipeline Contaminated with Sewage", "Black dirty water is coming out of tap supply since morning. Sewage leak is mixing with main water line in Block 4.", "Water", "High", 78, "Pending"),
            ("Pothole near Sector 5 Traffic Light", "Huge pothole causing traffic jams and minor bike slippages during rain. Needs road resurfacing.", "Roads", "Medium", 48, "In Progress"),
            ("Garbage Overflowing in Ward 12", "Community dustbin is overflowing for 4 days. Bad odor and pest infestation growing.", "Sanitation", "Medium", 42, "Resolved"),
            ("Streetlight Defective on 3rd Cross Street", "Street light bulb is flickering and dark at night near the corner.", "Electricity", "Low", 22, "Resolved"),
            ("Request for Additional Bench in Community Park", "Elderly residents request 2 extra wooden benches in the main walking area of Green Park.", "Environment", "Low", 15, "Pending"),
        ]

        for title, desc, cat, prio, score, status in samples:
            cursor.execute("""
                INSERT INTO complaints (user_id, title, description, category, priority, priority_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, title, desc, cat, prio, score, status))

        conn.commit()
    conn.close()


# ================================================================== #
#  USER HELPERS
# ================================================================== #

def create_user(name, email, hashed_password, role='user'):
    """Insert a new user and return their id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, hashed_password, role)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email):
    """Fetch a user row by email (returns sqlite3.Row or None)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Fetch a user row by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_all_users():
    """Return all registered users (excluding admins)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = 'user' ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    return users


# ================================================================== #
#  COMPLAINT HELPERS
# ================================================================== #

def create_complaint(user_id, title, description, category, priority, priority_score):
    """Insert a new complaint and return its id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints
            (user_id, title, description, category, priority, priority_score, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
    """, (user_id, title, description, category, priority, priority_score))
    conn.commit()
    complaint_id = cursor.lastrowid
    conn.close()
    return complaint_id


def get_complaint_by_id(complaint_id):
    """Fetch a single complaint with user info."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, u.name as user_name, u.email as user_email
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    """, (complaint_id,))
    complaint = cursor.fetchone()
    conn.close()
    return complaint


def get_complaints_by_user(user_id):
    """Fetch all complaints submitted by a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM complaints
        WHERE user_id = ?
        ORDER BY priority_score DESC, created_at DESC
    """, (user_id,))
    complaints = cursor.fetchall()
    conn.close()
    return complaints


def get_all_complaints(category=None, status=None, priority=None, search=None):
    """
    Fetch all complaints with optional filters.
    Sorted by priority_score DESC (critical first).
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT c.*, u.name as user_name, u.email as user_email
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND c.category = ?"
        params.append(category)
    if status:
        query += " AND c.status = ?"
        params.append(status)
    if priority:
        query += " AND c.priority = ?"
        params.append(priority)
    if search:
        query += " AND (c.title LIKE ? OR c.description LIKE ? OR u.name LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])

    query += " ORDER BY c.priority_score DESC, c.created_at DESC"

    cursor.execute(query, params)
    complaints = cursor.fetchall()
    conn.close()
    return complaints


def update_complaint_status(complaint_id, new_status):
    """Update the status of a complaint."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints
        SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (new_status, complaint_id))
    conn.commit()
    conn.close()


def delete_complaint(complaint_id):
    """Permanently delete a complaint."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()


# ================================================================== #
#  ANALYTICS HELPERS
# ================================================================== #

def get_stats():
    """Return aggregate statistics for the admin dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Total counts by status
    cursor.execute("SELECT COUNT(*) FROM complaints")
    stats['total'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
    stats['pending'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    stats['in_progress'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    stats['resolved'] = cursor.fetchone()[0]

    # Priority counts
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE priority = 'Critical'")
    stats['critical'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE priority = 'High'")
    stats['high'] = cursor.fetchone()[0]

    # Complaints by priority (for chart)
    cursor.execute("""
        SELECT priority, COUNT(*) as count
        FROM complaints GROUP BY priority
    """)
    stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}

    # Complaints by category (for chart)
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM complaints GROUP BY category ORDER BY count DESC
    """)
    stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}

    # Complaints by status (for chart)
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM complaints GROUP BY status
    """)
    stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

    # Monthly complaint count (last 6 months)
    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM complaints
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """)
    monthly = cursor.fetchall()
    stats['monthly_labels'] = [r['month'] for r in reversed(monthly)]
    stats['monthly_data']   = [r['count'] for r in reversed(monthly)]

    conn.close()
    return stats
