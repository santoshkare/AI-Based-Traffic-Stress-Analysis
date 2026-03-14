# SafeDrive.ai - Configuration Guide

This guide explains how to configure SafeDrive.ai for your specific needs.

---

## Configuration Files

### 1. Backend Configuration

**File:** `backend/app.py`

Key settings:

```python
# Session timeout (seconds)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Enable/disable secure cookies
app.config['SESSION_COOKIE_SECURE'] = True  # Set False for development

# CORS allowed origins
CORS(app, supports_credentials=True)
```

### 2. Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Security
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development  # Change to 'production' for deployment
FLASK_DEBUG=True       # Set to False in production

# Server settings
PORT=5000
HOST=0.0.0.0

# Database (optional)
DATABASE_URL=sqlite:///safedrive.db

# Detection settings
MIN_DETECTION_CONFIDENCE=0.5
MIN_TRACKING_CONFIDENCE=0.5

# Logging
LOG_LEVEL=INFO
LOG_FILE=safedrive.log
```

Load in your Python code:

```python
import os
from dotenv import load_dotenv

load_dotenv()
secret_key = os.getenv('SECRET_KEY', 'default-secret')
```

---

## Detection Module Configuration

### Drowsiness Detection

**File:** `backend/drowsiness_detection.py`

```python
# Thresholds (tune for sensitivity)
EAR_THRESH = 0.25    # Eye Aspect Ratio threshold (lower = more sensitive)
MAR_THRESH = 0.60    # Mouth Aspect Ratio threshold (higher = more sensitive)

# Consecutive frames required for detection
EAR_CONSEC = 18      # Frames eyes must be closed to trigger drowsiness
MAR_CONSEC = 12      # Frames mouth must be open to trigger yawning
```

### Risk Engine Configuration

**File:** `backend/risk_engine.py`

```python
# Risk score weights (sum should equal 1.0)
WEIGHTS = {
    "drowsiness": 0.35,    # 35% weight
    "stress": 0.25,        # 25% weight
    "environment": 0.20,   # 20% weight
    "child": 0.20          # 20% weight
}

# Rolling average window size (frames)
window = 30  # Larger = smoother but slower response

# Alert thresholds
HIGH_RISK_THRESHOLD = 6.0
MEDIUM_RISK_THRESHOLD = 3.0
```

Customize weights based on your priorities:

```python
# High drowsiness focus (e.g., night driving)
WEIGHTS = {
    "drowsiness": 0.50,  # Increased to 50%
    "stress": 0.20,
    "environment": 0.15,
    "child": 0.15
}
```

---

## Frontend Configuration

### Appearance

**File:** `frontend/index.html`

CSS Variables (change in `<style>` section):

```css
:root {
  --bg: #080c14; /* Main background */
  --panel: #0d1220; /* Panel background */
  --border: #1c2a40; /* Border color */
  --text: #c0d0e8; /* Text color */
  --red: #e74c3c; /* Alert color */
  --yellow: #f0a500; /* Warning color */
  --green: #22c55e; /* Safe color */
  --blue: #3b82f6; /* Info color */
}
```

### Layout Configuration

Modify grid layout:

```css
.wrap {
  grid-template-columns: 190px 1fr 280px; /* Sidebar width, Center, Right panel */
  gap: 8px;
}
```

### Camera Feed Settings

In JavaScript:

```javascript
// Adjust camera resolution
const video = document.getElementById("vid");
video.width = 1280; // Default: 1280
video.height = 720; // Default: 720
```

---

## Credential Management

### Default Users

**File:** `backend/app.py`

Change default credentials:

```python
USERS = {
    "admin@safedrive.ai": {"password": _h("change_this_password"), "name": "Admin"},
    "demo@test.com": {"password": _h("change_this_password"), "name": "Demo"},
}
```

### Adding New Users

Option 1: Add to USERS dict directly:

```python
USERS["newemail@example.com"] = {
    "password": _h("newpassword"),
    "name": "New User"
}
```

Option 2: Through registration endpoint:

```bash
# POST /api/register
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "password123"
}
```

---

## Logging Configuration

### Log Levels

**File:** `backend/app.py`

```python
import logging

# Set logging level
logging.basicConfig(level=logging.INFO)  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Create logger
logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

### Log Output Locations

```python
# Console output (terminal)
logging.StreamHandler()

# File output
logging.FileHandler('safedrive.log')

# Custom log file
logging.FileHandler('logs/safedrive_' + date_string + '.log')
```

---

## Performance Tuning

### Reduce Processing Load

```python
# Process every Nth frame (in run_all.py)
frame_count = 0
frame_skip = 2  # Process every 2nd frame

frame_count += 1
if frame_count % frame_skip == 0:
    results = detector.process(frame)
```

### Adjust Detection Confidence

Lower = faster but less accurate, Higher = slower but more accurate

```python
# In drowsiness_detection.py
FaceMesh(
    min_detection_confidence=0.3,   # Lower = faster
    min_tracking_confidence=0.3,
)
```

### Memory Optimization

```python
# Limit event history
EVENTS = []  # Default keeps all events

# Add auto-cleanup (example)
if len(EVENTS) > 10000:
    EVENTS = EVENTS[-5000:]  # Keep last 5000 events
```

---

## Integration Configuration

### Custom API Endpoints

Add new endpoints to `backend/app.py`:

```python
@app.route("/api/custom_endpoint", methods=["POST"])
def custom_endpoint():
    data = request.get_json(silent=True) or {}
    # Your custom logic here
    return jsonify({"ok": True, "result": "data"})
```

### Database Integration

Replace in-memory storage with database:

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safedrive.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
```

---

## Development vs Production

### Development Configuration

```python
# app.py
FLASK_ENV = "development"
FLASK_DEBUG = True
SESSION_COOKIE_SECURE = False
app.run(debug=True)
```

### Production Configuration

```python
# .env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<long-random-string>

# app.py
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
app.run(debug=False)
```

---

## Common Configuration Scenarios

### Scenario 1: Night Driving Detection

```python
# Increase sensitivity to drowsiness
EAR_THRESH = 0.20  # More sensitive
EAR_CONSEC = 12    # Faster response

# Increase drowsiness weight
WEIGHTS["drowsiness"] = 0.50
```

### Scenario 2: Multi-Driver Fleet

```python
# Add database for persistence
# Increase session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = 28800  # 8 hours

# Add per-user event tracking
```

### Scenario 3: Low-Latency System

```python
# Skip frames for speed
frame_skip = 3

# Lower detection confidence
min_detection_confidence = 0.3

# Smaller risk window
window = 15  # Instead of 30
```

---

## Checking Configuration

View active configuration:

```bash
# Check Flask environment variables
echo $FLASK_ENV
echo $FLASK_DEBUG

# View Python configuration
python -c "from app import app; print(app.config)"
```

---

## Resetting to Defaults

To reset all configurations to defaults:

1. Restore original files from backup
2. Delete `.env` file
3. Restart the application

```bash
# If using git
git checkout backend/app.py
rm backend/.env
```
