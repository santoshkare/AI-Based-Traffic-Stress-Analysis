"""
SafeDrive.ai - Flask Web Server
================================
Run:  python app.py
Open: http://localhost:5000
"""

import os
import hashlib
import time
import logging
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
from functools import wraps

THIS_DIR     = Path(__file__).parent           # .../backend
FRONTEND_DIR = THIS_DIR.parent / "frontend"    # .../frontend

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "safedrive_secret_2024")
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
CORS(app, supports_credentials=True)

# ── Logging Setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('safedrive.log')
    ]
)
logger = logging.getLogger(__name__)

# ── User store ────────────────────────────────────────────────
def _h(pw): 
    """Hash password using SHA256"""
    return hashlib.sha256(pw.encode()).hexdigest()

def _is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def _is_valid_password(pw):
    """Check password strength (min 8 chars, at least 1 letter and 1 number)"""
    return len(pw) >= 8

def _sanitize_input(text, max_len=100):
    """Remove potentially harmful characters from input"""
    if not isinstance(text, str):
        return ""
    return text.strip()[:max_len]

USERS = {
    "admin@safedrive.ai": {"password": _h("admin123"), "name": "Admin User"},
    "demo@test.com":      {"password": _h("demo1234"), "name": "Demo Driver"},
}
EVENTS = []
LOGIN_ATTEMPTS = {}  # Track failed login attempts

# ── Decorators ─────────────────────────────────────────────────
def require_login(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated

# ── Frontend serving ──────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")

@app.route("/<path:filename>")
def assets(filename):
    return send_from_directory(str(FRONTEND_DIR), filename)

# ── Auth API ──────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate user with email and password"""
    try:
        d     = request.get_json(silent=True) or {}
        email = _sanitize_input(d.get("email", "")).lower()
        pw    = d.get("password", "")
        
        # Rate limiting
        email_lower = email.lower()
        if email_lower in LOGIN_ATTEMPTS:
            attempts, last_time = LOGIN_ATTEMPTS[email_lower]
            if attempts >= 5 and time.time() - last_time < 300:
                logger.warning(f"Too many login attempts for {email}")
                return jsonify({"ok": False, "error": "Too many attempts. Try again later."}), 429
        
        if not email or not pw:
            return jsonify({"ok": False, "error": "Email and password required"}), 400
        
        if not _is_valid_email(email):
            return jsonify({"ok": False, "error": "Invalid email format"}), 400
        
        user = USERS.get(email)
        if not user or user["password"] != _h(pw):
            LOGIN_ATTEMPTS[email] = (LOGIN_ATTEMPTS.get(email, (0, time.time()))[0] + 1, time.time())
            logger.warning(f"Failed login attempt for {email}")
            return jsonify({"ok": False, "error": "Invalid email or password"}), 401
        
        # Clear failed attempts on success
        LOGIN_ATTEMPTS.pop(email, None)
        session.permanent = True
        session["user"] = {"email": email, "name": user["name"]}
        logger.info(f"User logged in: {email}")
        return jsonify({"ok": True, "name": user["name"]})
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/register", methods=["POST"])
def register():
    """Register new user account"""
    try:
        d     = request.get_json(silent=True) or {}
        email = _sanitize_input(d.get("email", "")).lower()
        name  = _sanitize_input(d.get("name", ""), max_len=50)
        pw    = d.get("password", "")
        
        if not email or not name or not pw:
            return jsonify({"ok": False, "error": "All fields required"}), 400
        
        if not _is_valid_email(email):
            return jsonify({"ok": False, "error": "Invalid email format"}), 400
        
        if not _is_valid_password(pw):
            return jsonify({"ok": False, "error": "Password must be at least 8 characters"}), 400
        
        if email in USERS:
            logger.warning(f"Registration attempt with existing email: {email}")
            return jsonify({"ok": False, "error": "Email already registered"}), 409
        
        USERS[email] = {"password": _h(pw), "name": name}
        session.permanent = True
        session["user"] = {"email": email, "name": name}
        logger.info(f"New user registered: {email}")
        return jsonify({"ok": True, "name": name})
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    """Logout current user"""
    try:
        email = session.get("user", {}).get("email", "unknown")
        session.clear()
        logger.info(f"User logged out: {email}")
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/log_event", methods=["POST"])
@require_login
def log_event():
    """Log a driver event (requires authentication)"""
    try:
        d = request.get_json(silent=True) or {}
        event_type = _sanitize_input(d.get("type", ""))
        score = d.get("score", 0)
        
        if not event_type:
            return jsonify({"ok": False, "error": "Event type required"}), 400
        
        if not isinstance(score, (int, float)) or score < 0 or score > 10:
            return jsonify({"ok": False, "error": "Invalid score (0-10)"}), 400
        
        event = {
            "ts": time.strftime("%H:%M:%S"),
            "user": session["user"]["email"],
            "type": event_type,
            "score": round(score, 2)
        }
        EVENTS.append(event)
        logger.info(f"Event logged by {session['user']['email']}: {event_type}={score}")
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Log event error: {str(e)}")
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/stats")
@require_login
def stats():
    """Get system statistics (requires authentication)"""
    try:
        return jsonify({
            "ok": True,
            "events": len(EVENTS),
            "users": len(USERS),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({"ok": False, "error": "Server error"}), 500

# ── Error handlers ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 not found: {request.path}")
    return jsonify({"ok": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({"ok": False, "error": "Internal server error"}), 500

# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 52)
    print("  SafeDrive.ai  —  Flask Server")
    print(f"  Frontend : {FRONTEND_DIR}")
    print(f"  Exists   : {FRONTEND_DIR.exists()}")
    print("  URL      : http://localhost:5000")
    print("  Credentials:")
    print("    - admin@safedrive.ai / admin123")
    print("    - demo@test.com / demo1234")
    print("=" * 52)
    logger.info("SafeDrive.ai Flask server starting")
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
