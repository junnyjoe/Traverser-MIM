"""
Database module for the Bible Verse Drawing Application.
Supports both SQLite (local development) and PostgreSQL (production).
"""

import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

# Check if we're using PostgreSQL (production) or SQLite (local dev)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production: Use PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = True
else:
    # Local development: Use SQLite
    import sqlite3
    USE_POSTGRES = False
    DB_PATH = os.path.join(os.path.dirname(__file__), 'verset.db')


def get_connection():
    """Create and return a database connection."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def get_cursor(conn):
    """Get a cursor with appropriate settings."""
    if USE_POSTGRES:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        return conn.cursor()


def placeholder():
    """Return the correct placeholder for SQL queries."""
    return "%s" if USE_POSTGRES else "?"


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = get_cursor(conn)
    
    # Create verses table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verses (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                reference TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                reference TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Create user_draws table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_draws (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                verse_id INTEGER NOT NULL,
                first_name TEXT,
                last_name TEXT,
                drawn_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (verse_id) REFERENCES verses(id)
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_draws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                verse_id INTEGER NOT NULL,
                first_name TEXT,
                last_name TEXT,
                drawn_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (verse_id) REFERENCES verses(id)
            )
        ''')
    
    # Create admin table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
    
    conn.commit()
    
    # Insert default admin if not exists
    p = placeholder()
    cursor.execute('SELECT COUNT(*) as count FROM admin')
    row = cursor.fetchone()
    count = row['count'] if USE_POSTGRES else row[0]
    
    if count == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute(
            f'INSERT INTO admin (username, password_hash) VALUES ({p}, {p})',
            ('admin', password_hash)
        )
    
    # Insert sample verses if none exist
    cursor.execute('SELECT COUNT(*) as count FROM verses')
    row = cursor.fetchone()
    count = row['count'] if USE_POSTGRES else row[0]
    
    if count == 0:
        sample_verses = [
            ("Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle.", "Jean 3:16"),
            ("L'Éternel est mon berger: je ne manquerai de rien.", "Psaume 23:1"),
            ("Je puis tout par celui qui me fortifie.", "Philippiens 4:13"),
            ("Confie-toi en l'Éternel de tout ton cœur, Et ne t'appuie pas sur ta sagesse.", "Proverbes 3:5"),
            ("Car je connais les projets que j'ai formés sur vous, dit l'Éternel, projets de paix et non de malheur, afin de vous donner un avenir et de l'espérance.", "Jérémie 29:11"),
            ("Ne crains point, car je suis avec toi; Ne promène pas des regards inquiets, car je suis ton Dieu.", "Ésaïe 41:10"),
            ("Venez à moi, vous tous qui êtes fatigués et chargés, et je vous donnerai du repos.", "Matthieu 11:28"),
            ("L'amour est patient, il est plein de bonté; l'amour n'est point envieux; l'amour ne se vante point.", "1 Corinthiens 13:4"),
        ]
        for text, reference in sample_verses:
            cursor.execute(
                f'INSERT INTO verses (text, reference) VALUES ({p}, {p})',
                (text, reference)
            )
    
    conn.commit()
    conn.close()


# ============== VERSE OPERATIONS ==============

def get_all_verses():
    """Get all verses from the database."""
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute('SELECT id, text, reference, created_at FROM verses ORDER BY id DESC')
    verses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return verses


def add_verse(text, reference):
    """Add a new verse to the database."""
    conn = get_connection()
    cursor = get_cursor(conn)
    p = placeholder()
    
    if USE_POSTGRES:
        cursor.execute(
            f'INSERT INTO verses (text, reference) VALUES ({p}, {p}) RETURNING id',
            (text, reference)
        )
        verse_id = cursor.fetchone()['id']
    else:
        cursor.execute(
            f'INSERT INTO verses (text, reference) VALUES ({p}, {p})',
            (text, reference)
        )
        verse_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return verse_id


def delete_verse(verse_id):
    """Delete a verse by its ID."""
    conn = get_connection()
    cursor = get_cursor(conn)
    p = placeholder()
    cursor.execute(f'DELETE FROM verses WHERE id = {p}', (verse_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_verse_by_id(verse_id):
    """Get a specific verse by ID."""
    conn = get_connection()
    cursor = get_cursor(conn)
    p = placeholder()
    cursor.execute(f'SELECT id, text, reference FROM verses WHERE id = {p}', (verse_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============== USER DRAW OPERATIONS ==============

def check_user_draw(email):
    """Check if a user has already drawn a verse."""
    conn = get_connection()
    cursor = get_cursor(conn)
    p = placeholder()
    cursor.execute(f'''
        SELECT v.id, v.text, v.reference, ud.drawn_at, ud.first_name, ud.last_name
        FROM user_draws ud
        JOIN verses v ON ud.verse_id = v.id
        WHERE ud.email = {p}
    ''', (email.lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def draw_verse_for_user(email, first_name=None, last_name=None):
    """Draw a random verse for a user."""
    email = email.lower().strip()
    
    # Check if user already drew
    existing = check_user_draw(email)
    if existing:
        return {
            'verse': existing,
            'already_drawn': True
        }
    
    # Get all available verses
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute('SELECT id, text, reference FROM verses')
    verses = cursor.fetchall()
    
    if not verses:
        conn.close()
        return None
    
    # Pick a random verse
    chosen = random.choice(verses)
    chosen_dict = dict(chosen)
    
    # Save the draw
    p = placeholder()
    cursor.execute(
        f'INSERT INTO user_draws (email, verse_id, first_name, last_name) VALUES ({p}, {p}, {p}, {p})',
        (email, chosen_dict['id'], first_name, last_name)
    )
    conn.commit()
    conn.close()
    
    return {
        'verse': chosen_dict,
        'already_drawn': False
    }


# ============== ADMIN OPERATIONS ==============

def verify_admin(username, password):
    """Verify admin credentials."""
    conn = get_connection()
    cursor = get_cursor(conn)
    p = placeholder()
    cursor.execute(
        f'SELECT id, password_hash FROM admin WHERE username = {p}',
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        row_dict = dict(row)
        if check_password_hash(row_dict['password_hash'], password):
            return row_dict['id']
    return None


def get_draw_stats():
    """Get statistics about draws."""
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute('SELECT COUNT(*) as total FROM user_draws')
    row = cursor.fetchone()
    total_draws = dict(row)['total'] if USE_POSTGRES else row[0]
    cursor.execute('SELECT COUNT(*) as total FROM verses')
    row = cursor.fetchone()
    total_verses = dict(row)['total'] if USE_POSTGRES else row[0]
    conn.close()
    return {
        'total_draws': total_draws,
        'total_verses': total_verses
    }


def get_all_draws():
    """Return all draws with email, verse id, drawn_at and verse reference/text."""
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute('''
        SELECT ud.email, ud.verse_id, ud.drawn_at, ud.first_name, ud.last_name, v.text, v.reference
        FROM user_draws ud
        JOIN verses v ON ud.verse_id = v.id
        ORDER BY ud.drawn_at DESC
    ''')
    draws = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return draws
