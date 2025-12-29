"""
Bible Verse Drawing Application - Main Flask Application
A simple web app allowing users to draw one verse per email,
with an admin interface for verse management.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database operations
import database

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API calls

# Load secret key from environment (required in production)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise RuntimeError('Environment variable SECRET_KEY is required. Set SECRET_KEY before starting the app.')
app.secret_key = secret_key

# Initialize database on startup
database.init_db()


# ============== EMAIL VALIDATION ==============

def is_valid_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ============== PAGE ROUTES ==============

@app.route('/')
def index():
    """Serve the homepage."""
    return render_template('index.html')


@app.route('/admin')
def admin():
    """Serve the admin page."""
    return render_template('admin.html')


# ============== USER API ROUTES ==============

@app.route('/api/draw-verse', methods=['POST'])
def draw_verse():
    """
    API endpoint to draw a verse for a user.
    Requires: { "email": "user@example.com" }
    Returns: { "success": true, "verse": {...}, "already_drawn": bool }
    """
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({
            'success': False,
            'error': 'Email requis'
        }), 400
    
    email = data['email'].strip()
    
    # Validate email format
    if not is_valid_email(email):
        return jsonify({
            'success': False,
            'error': 'Format d\'email invalide'
        }), 400
    
    # Draw verse for user (accept optional first/last name)
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    result = database.draw_verse_for_user(email, first_name=first_name or None, last_name=last_name or None)
    
    if result is None:
        return jsonify({
            'success': False,
            'error': 'Aucun verset disponible. Contactez l\'administrateur.'
        }), 404
    
    return jsonify({
        'success': True,
        'verse': result['verse'],
        'already_drawn': result['already_drawn']
    })


# ============== ADMIN API ROUTES ==============

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """
    Admin login endpoint.
    Requires: { "username": "admin", "password": "..." }
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Nom d\'utilisateur et mot de passe requis'
        }), 400
    
    admin_id = database.verify_admin(data['username'], data['password'])
    
    if admin_id:
        session['admin_id'] = admin_id
        session['admin_logged_in'] = True
        return jsonify({
            'success': True,
            'message': 'Connexion réussie'
        })
    
    return jsonify({
        'success': False,
        'error': 'Identifiants incorrects'
    }), 401


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint."""
    session.clear()
    return jsonify({'success': True})


@app.route('/api/admin/check', methods=['GET'])
def admin_check():
    """Check if admin is logged in."""
    is_logged_in = session.get('admin_logged_in', False)
    return jsonify({'logged_in': is_logged_in})


@app.route('/api/admin/verses', methods=['GET'])
def get_verses():
    """Get all verses (admin only)."""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Non autorisé'}), 401
    
    verses = database.get_all_verses()
    stats = database.get_draw_stats()
    
    return jsonify({
        'success': True,
        'verses': verses,
        'stats': stats
    })


@app.route('/api/admin/draws', methods=['GET'])
def admin_draws():
    """Get all user draws (admin only)."""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Non autorisé'}), 401

    draws = database.get_all_draws()
    return jsonify({
        'success': True,
        'draws': draws
    })


@app.route('/api/admin/verses', methods=['POST'])
def add_verse():
    """Add a new verse (admin only)."""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Non autorisé'}), 401
    
    data = request.get_json()
    
    if not data or 'text' not in data or 'reference' not in data:
        return jsonify({
            'success': False,
            'error': 'Texte et référence requis'
        }), 400
    
    text = data['text'].strip()
    reference = data['reference'].strip()
    
    if not text or not reference:
        return jsonify({
            'success': False,
            'error': 'Le texte et la référence ne peuvent pas être vides'
        }), 400
    
    verse_id = database.add_verse(text, reference)
    
    return jsonify({
        'success': True,
        'verse_id': verse_id,
        'message': 'Verset ajouté avec succès'
    })


@app.route('/api/admin/verses/<int:verse_id>', methods=['DELETE'])
def delete_verse(verse_id):
    """Delete a verse (admin only)."""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Non autorisé'}), 401
    
    deleted = database.delete_verse(verse_id)
    
    if deleted:
        return jsonify({
            'success': True,
            'message': 'Verset supprimé'
        })
    
    return jsonify({
        'success': False,
        'error': 'Verset non trouvé'
    }), 404


# ============== RUN APPLICATION ==============

if __name__ == '__main__':
    debug_flag = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("Bible Verse Drawing Application")
    print("=" * 50)
    print(f"User page: http://localhost:{port}")
    print(f"Admin page: http://localhost:{port}/admin")
    print("   Default login: admin / admin123")
    print(f"Starting with DEBUG={debug_flag}")
    print("=" * 50)
    app.run(debug=debug_flag, host='0.0.0.0', port=port)
