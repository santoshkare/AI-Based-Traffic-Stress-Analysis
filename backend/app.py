"""
SafeDrive.ai v3.0 — Flask Backend
===================================
Run:  python app.py
Open: http://localhost:5000

Features:
  - Secure session management with rate limiting
  - Event logging with JSON persistence
  - Real-time stats aggregation
  - Driver session tracking
  - Alert history endpoint
  - Health-check endpoint
"""

import os, json, hashlib, time, logging, re
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS

# ── Paths ─────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).parent
FRONTEND_DIR = THIS_DIR.parent / "frontend"
DATA_FILE    = THIS_DIR / "events.json"
LOG_FILE     = THIS_DIR / "safedrive.log"

# ── App ───────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key          = os.environ.get("SECRET_KEY", "safedrive_v3_secret_2025_change_in_prod")
app.config.update(
    SESSION_COOKIE_HTTPONLY  = True,
    SESSION_COOKIE_SAMESITE  = "Lax",
    SESSION_COOKIE_SECURE    = False,   # Set True when using HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8),
)
CORS(app, supports_credentials=True, origins="*")

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger("safedrive")

# ── Helpers ───────────────────────────────────────────────────
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w.%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$", email))

def _sanitize(text, max_len=120) -> str:
    if not isinstance(text, str): return ""
    return text.strip()[:max_len]

# ── In-memory stores ──────────────────────────────────────────
USERS: dict = {
    "admin@safedrive.ai": {"password": _hash("admin123"),  "name": "Admin",       "role": "admin"},
    "demo@test.com":      {"password": _hash("demo1234"),  "name": "Demo Driver",  "role": "driver"},
    "test@driver.com":    {"password": _hash("test1234"),  "name": "Test Driver",  "role": "driver"},
}

EVENTS: list = []          # [{ts, user, type, score, session_id}]
LOGIN_ATTEMPTS: dict = {}  # {email: (count, last_time)}
DRIVER_SESSIONS: dict = {} # {session_id: {start, end, user, events, max_risk}}

# ── Load persisted events ─────────────────────────────────────
if DATA_FILE.exists():
    try:
        with open(DATA_FILE) as f:
            EVENTS = json.load(f)
        log.info(f"Loaded {len(EVENTS)} historical events")
    except Exception as e:
        log.warning(f"Could not load events.json: {e}")

def _save_events():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(EVENTS[-5000:], f, indent=2)   # Keep last 5000
    except Exception as e:
        log.error(f"Could not save events: {e}")

# ── Decorators ────────────────────────────────────────────────
def require_login(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return wrapped

def require_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        if session["user"].get("role") != "admin":
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapped

# ── Frontend serving ──────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")

@app.route("/<path:filename>")
def assets(filename):
    return send_from_directory(str(FRONTEND_DIR), filename)

# ── Auth ──────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    try:
        d     = request.get_json(silent=True) or {}
        email = _sanitize(d.get("email","")).lower()
        pw    = d.get("password","")

        if not email or not pw:
            return jsonify({"ok": False, "error": "Email and password required"}), 400
        if not _valid_email(email):
            return jsonify({"ok": False, "error": "Invalid email format"}), 400

        # Rate limiting
        now = time.time()
        att = LOGIN_ATTEMPTS.get(email, (0, 0))
        if att[0] >= 5 and now - att[1] < 300:
            remaining = int(300 - (now - att[1]))
            return jsonify({"ok": False, "error": f"Account locked. Try again in {remaining}s"}), 429

        user = USERS.get(email)
        if not user or user["password"] != _hash(pw):
            LOGIN_ATTEMPTS[email] = (att[0] + 1, now)
            log.warning(f"Failed login: {email} (attempt {att[0]+1})")
            return jsonify({"ok": False, "error": "Invalid email or password"}), 401

        LOGIN_ATTEMPTS.pop(email, None)
        session.permanent = True
        session["user"] = {"email": email, "name": user["name"], "role": user.get("role","driver")}
        log.info(f"Login: {email}")

        # Start driver session
        sid = f"{email}_{int(now)}"
        DRIVER_SESSIONS[sid] = {"session_id": sid, "user": email, "start": now,
                                  "end": None, "events": 0, "max_risk": 0.0,
                                  "alerts": 0}
        session["driver_session"] = sid

        return jsonify({"ok": True, "name": user["name"], "role": user.get("role","driver")})
    except Exception as e:
        log.error(f"Login error: {e}")
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/register", methods=["POST"])
def register():
    try:
        d     = request.get_json(silent=True) or {}
        email = _sanitize(d.get("email","")).lower()
        name  = _sanitize(d.get("name",""), max_len=50)
        pw    = d.get("password","")

        if not email or not name or not pw:
            return jsonify({"ok": False, "error": "All fields required"}), 400
        if not _valid_email(email):
            return jsonify({"ok": False, "error": "Invalid email format"}), 400
        if len(pw) < 8:
            return jsonify({"ok": False, "error": "Password must be at least 8 characters"}), 400
        if email in USERS:
            return jsonify({"ok": False, "error": "Email already registered"}), 409

        USERS[email] = {"password": _hash(pw), "name": name, "role": "driver"}
        session.permanent = True
        session["user"] = {"email": email, "name": name, "role": "driver"}
        log.info(f"New user registered: {email}")
        return jsonify({"ok": True, "name": name})
    except Exception as e:
        log.error(f"Register error: {e}")
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    email = session.get("user", {}).get("email", "unknown")
    sid   = session.get("driver_session")
    if sid and sid in DRIVER_SESSIONS:
        DRIVER_SESSIONS[sid]["end"] = time.time()
    session.clear()
    log.info(f"Logout: {email}")
    return jsonify({"ok": True})

@app.route("/api/me")
@require_login
def me():
    return jsonify({"ok": True, "user": session["user"]})

# ── Event logging ─────────────────────────────────────────────
@app.route("/api/log_event", methods=["POST"])
@require_login
def log_event():
    try:
        d          = request.get_json(silent=True) or {}
        event_type = _sanitize(d.get("type",""))
        score      = d.get("score", 0)
        details    = d.get("details", {})

        if not event_type:
            return jsonify({"ok": False, "error": "Event type required"}), 400
        if not isinstance(score, (int, float)) or not (0 <= score <= 10):
            return jsonify({"ok": False, "error": "Score must be 0-10"}), 400

        now   = time.time()
        event = {
            "ts":         datetime.fromtimestamp(now).strftime("%H:%M:%S"),
            "date":       datetime.fromtimestamp(now).strftime("%Y-%m-%d"),
            "epoch":      now,
            "user":       session["user"]["email"],
            "type":       event_type,
            "score":      round(float(score), 2),
            "details":    details,
            "session_id": session.get("driver_session",""),
        }
        EVENTS.append(event)

        # Update driver session stats
        sid = session.get("driver_session","")
        if sid and sid in DRIVER_SESSIONS:
            DRIVER_SESSIONS[sid]["events"] += 1
            if score > DRIVER_SESSIONS[sid]["max_risk"]:
                DRIVER_SESSIONS[sid]["max_risk"] = score
            if event_type in ("high_risk", "drowsiness", "child_alert"):
                DRIVER_SESSIONS[sid]["alerts"] += 1

        # Persist every 50 events
        if len(EVENTS) % 50 == 0:
            _save_events()

        return jsonify({"ok": True})
    except Exception as e:
        log.error(f"Log event error: {e}")
        return jsonify({"ok": False, "error": "Server error"}), 500

# ── Stats ─────────────────────────────────────────────────────
@app.route("/api/stats")
@require_login
def stats():
    try:
        user_email = session["user"]["email"]
        user_events = [e for e in EVENTS if e["user"] == user_email]
        today       = datetime.now().strftime("%Y-%m-%d")
        today_events= [e for e in user_events if e.get("date") == today]

        scores      = [e["score"] for e in user_events if e["score"] > 0]
        avg_risk    = round(sum(scores) / len(scores), 2) if scores else 0
        max_risk    = round(max(scores), 2) if scores else 0

        type_counts: dict = {}
        for e in user_events:
            type_counts[e["type"]] = type_counts.get(e["type"], 0) + 1

        # Recent 20 events for chart
        recent = sorted(user_events, key=lambda x: x.get("epoch",0), reverse=True)[:20]

        return jsonify({
            "ok": True,
            "total_events":  len(user_events),
            "today_events":  len(today_events),
            "total_users":   len(USERS),
            "avg_risk":      avg_risk,
            "max_risk":      max_risk,
            "type_counts":   type_counts,
            "recent_events": recent,
            "timestamp":     datetime.now().isoformat(),
        })
    except Exception as e:
        log.error(f"Stats error: {e}")
        return jsonify({"ok": False, "error": "Server error"}), 500

# ── Driver session ────────────────────────────────────────────
@app.route("/api/session_summary")
@require_login
def session_summary():
    sid = session.get("driver_session","")
    ds  = DRIVER_SESSIONS.get(sid)
    if not ds:
        return jsonify({"ok": True, "summary": None})
    duration = int(time.time() - ds["start"])
    return jsonify({
        "ok": True,
        "summary": {
            "duration_seconds": duration,
            "duration_fmt": f"{duration//3600:02d}:{(duration%3600)//60:02d}:{duration%60:02d}",
            "events":     ds["events"],
            "max_risk":   round(ds["max_risk"], 1),
            "alerts":     ds["alerts"],
        }
    })

# ── Health check ──────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({
        "ok":      True,
        "status":  "healthy",
        "version": "3.0",
        "uptime":  time.time(),
        "users":   len(USERS),
        "events":  len(EVENTS),
    })

# ── Admin: all sessions ───────────────────────────────────────
@app.route("/api/admin/sessions")
@require_admin
def admin_sessions():
    return jsonify({"ok": True, "sessions": list(DRIVER_SESSIONS.values())})

# ── Error handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"ok": False, "error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    log.error(f"500 error: {e}")
    return jsonify({"ok": False, "error": "Internal server error"}), 500

# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  SafeDrive.ai v3.0  —  Flask Server")
    print(f"  Frontend : {FRONTEND_DIR}")
    print("  URL      : http://localhost:5000")
    print("  Accounts :")
    print("    admin@safedrive.ai / admin123")
    print("    demo@test.com      / demo1234")
    print("    test@driver.com    / test1234")
    print("=" * 60)
    log.info("SafeDrive.ai v3.0 starting")
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        _save_events()
        log.info("Server stopped — events saved")
