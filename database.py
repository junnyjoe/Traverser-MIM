"""
Database module for the Bible Verse Drawing Application.
Handles SQLite database initialization and CRUD operations.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'verset.db')


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create verses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            reference TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_draws table (tracks which user drew which verse)
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Insert default admin if not exists
    cursor.execute('SELECT COUNT(*) FROM admin')
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO admin (username, password_hash) VALUES (?, ?)',
            ('admin', password_hash)
        )
    
    # Insert some sample verses if none exist
    cursor.execute('SELECT COUNT(*) FROM verses')
    if cursor.fetchone()[0] == 0:
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
        cursor.executemany(
            'INSERT INTO verses (text, reference) VALUES (?, ?)',
            sample_verses
        )
    
    conn.commit()
    conn.close()

    # Ensure columns exist for older DBs (migrations)
    conn2 = get_connection()
    cur2 = conn2.cursor()
    cur2.execute("PRAGMA table_info(user_draws)")
    cols = [r['name'] for r in cur2.fetchall()]
    # Add first_name and last_name if missing
    if 'first_name' not in cols:
        cur2.execute('ALTER TABLE user_draws ADD COLUMN first_name TEXT')
    if 'last_name' not in cols:
        cur2.execute('ALTER TABLE user_draws ADD COLUMN last_name TEXT')
    conn2.commit()
    conn2.close()


# ============== VERSE OPERATIONS ==============

def get_all_verses():
    """Get all verses from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, text, reference, created_at FROM verses ORDER BY id DESC')
    verses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return verses


def add_verse(text, reference):
    """Add a new verse to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO verses (text, reference) VALUES (?, ?)',
        (text, reference)
    )
    verse_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return verse_id


def delete_verse(verse_id):
    """Delete a verse by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM verses WHERE id = ?', (verse_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_verse_by_id(verse_id):
    """Get a specific verse by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, text, reference FROM verses WHERE id = ?', (verse_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============== USER DRAW OPERATIONS ==============

def check_user_draw(email):
    """
    Check if a user has already drawn a verse.
    Returns the verse if already drawn, None otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, v.text, v.reference, ud.drawn_at, ud.first_name, ud.last_name
        FROM user_draws ud
        JOIN verses v ON ud.verse_id = v.id
        WHERE ud.email = ?
    ''', (email.lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def draw_verse_for_user(email, first_name=None, last_name=None):
    """
    Draw a random verse for a user.
    If user already has a verse, return that verse with already_drawn=True.
    Otherwise, draw a new random verse and save it.
    """
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
    cursor = conn.cursor()
    cursor.execute('SELECT id, text, reference FROM verses')
    verses = cursor.fetchall()
    
    if not verses:
        conn.close()
        return None
    
    # Pick a random verse
    chosen = random.choice(verses)
    
    # Save the draw (include names if provided)
    cursor.execute(
        'INSERT INTO user_draws (email, verse_id, first_name, last_name) VALUES (?, ?, ?, ?)',
        (email, chosen['id'], first_name, last_name)
    )
    conn.commit()
    conn.close()
    
    return {
        'verse': dict(chosen),
        'already_drawn': False
    }


# ============== ADMIN OPERATIONS ==============

def verify_admin(username, password):
    """Verify admin credentials."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, password_hash FROM admin WHERE username = ?',
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password_hash(row['password_hash'], password):
        return row['id']
    return None


def get_draw_stats():
    """Get statistics about draws."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM user_draws')
    total_draws = cursor.fetchone()['total']
    cursor.execute('SELECT COUNT(*) as total FROM verses')
    total_verses = cursor.fetchone()['total']
    conn.close()
    return {
        'total_draws': total_draws,
        'total_verses': total_verses
    }


def get_all_draws():
    """Return all draws with email, verse id, drawn_at and verse reference/text."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ud.email, ud.verse_id, ud.drawn_at, ud.first_name, ud.last_name, v.text, v.reference
        FROM user_draws ud
        JOIN verses v ON ud.verse_id = v.id
        ORDER BY ud.drawn_at DESC
    ''')
    draws = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return draws
