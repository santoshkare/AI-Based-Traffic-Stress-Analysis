# SafeDrive.ai - Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Edge, or Firefox)
- Webcam and microphone (for real-time detection)

---

## Installation Methods

### Method 1: Browser Installation (Simplest)

No Python installation needed! Just open the web dashboard.

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Open index.html in web browser
# On Windows: Right-click index.html → Open with → Chrome

# 3. Login with test credentials
# Email: demo@test.com
# Password: demo1234
```

**Requirements:**

- Modern browser (Chrome, Edge recommended)
- Local camera/microphone access

---

### Method 2: Flask Web Server

Run SafeDrive as a local web server for multi-device access.

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start the Flask server
cd backend
python app.py

# 3. Open in browser
# Visit: http://localhost:5000
```

**Features:**

- Multi-client access on local network
- Session management
- Event logging
- API endpoints

**Run on specific port:**

```bash
# Edit app.py and change port 5000 to your desired port
python app.py  # Then visit http://localhost:<your_port>
```

---

### Method 3: Python OpenCV Window (Direct Processing)

Real-time detection with direct OpenCV window display.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run detection modules
cd backend
python run_all.py

# 3. Keyboard controls
# E - Toggle engine ON/OFF
# R - Reset counters
# Q - Quit
```

**Individual module testing:**

```bash
# Test drowsiness detection
python drowsiness_detection.py

# Test emotion detection
python emotion_detection.py

# Test stress detection (console)
python stress_detection.py

# Test visibility detection
python visibility_detection.py
```

---

## Windows Batch Launcher

Use the provided `start.bat` file for easy startup.

```batch
# Double-click start.bat OR run from command prompt
start.bat
```

This will:

1. Install requirements
2. Launch Flask server
3. Open http://localhost:5000 in browser

---

## Docker Deployment

### Build Docker Image

```bash
# Build image
docker build -t safedrive:latest .

# Run container
docker run -p 5000:5000 \
  --device /dev/video0:/dev/video0 \
  safedrive:latest

# Access at http://localhost:5000
```

### Docker Compose (If available)

```bash
docker-compose up

# Stop
docker-compose down
```

---

## Environment Configuration

Create a `.env` file in the `backend` folder for custom settings:

```bash
# .env file
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0

# Model settings
MIN_DETECTION_CONFIDENCE=0.5
MIN_TRACKING_CONFIDENCE=0.5
```

Load in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.getenv('SECRET_KEY', 'default_secret')
```

---

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Access at http://localhost:5000
```

### Using WSGI Server

```bash
# Using waitress
pip install waitress

cd backend
waitress-serve --port=5000 app:app
```

---

## Security Checklist for Production

- [ ] Change default login credentials

  ```python
  # In backend/app.py
  USERS = {
      "your_email@company.com": {"password": _h("strong_password"), ...}
  }
  ```

- [ ] Set strong SECRET_KEY

  ```bash
  # Generate secure key
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] Enable HTTPS/SSL

  ```python
  # Use nginx or Apache reverse proxy
  # Configure SSL certificates
  ```

- [ ] Database backend (for production)
      Replace in-memory storage with SQLite/PostgreSQL:

  ```python
  # Use Flask-SQLAlchemy
  from flask_sqlalchemy import SQLAlchemy
  ```

- [ ] Add rate limiting

  ```python
  from flask_limiter import Limiter
  limiter = Limiter(app, key_func=lambda: request.remote_addr)
  ```

- [ ] Enable CORS selectively

  ```python
  CORS(app, origins=["https://your-domain.com"])
  ```

- [ ] Regular log monitoring
      Check `safedrive.log` for suspicious activity

---

## Troubleshooting

### Issue: "Cannot open camera"

**Solution:**

```bash
# Ensure camera is not in use by another application
# Try in a fresh browser tab
# On Windows: Settings → Privacy → Camera → Allow apps to access camera
```

### Issue: MediaPipe not found

**Solution:**

```bash
pip install --upgrade mediapipe
```

### Issue: Port 5000 already in use

**Solution:**

```bash
# Use different port
python -c "
from app import app
app.run(port=5001)
"
```

### Issue: CORS errors

**Ensure the browser origin is allowed:**

```python
# In app.py
CORS(app, origins=['http://localhost:5000'])
```

### Issue: Microphone not working

**Solution:**

- Check browser permissions (Settings → Loud)
- Grant microphone access when prompted
- Try Firefox CORS alternative

---

## Performance Optimization

### Reduce CPU Usage

```python
# In run_all.py, skip frames
if frame_count % 3 == 0:  # Process every 3rd frame
    results = detector.process(frame)
```

### GPU Acceleration (if available)

```python
# Enable GPU processing (requires CUDA)
import tensorflow as tf
# Configure GPU in detection modules
```

---

## Backing Up Data

```bash
# Backup event logs
cp safedrive.log safedrive_backup_$(date +%Y%m%d).log

# Backup configuration
cp backend/app.py backend/app_backup_$(date +%Y%m%d).py
```

---

## Monitoring & Logging

Access logs while running:

```bash
# Real-time log viewing
tail -f safedrive.log

# With timestamps
grep "2024-03-14" safedrive.log
```

Check for errors:

```bash
grep "ERROR" safedrive.log
```

---

## Performance Metrics

Expected performance on standard hardware:

- **Detection FPS:** 20-30 fps (1080p)
- **Latency:** 50-100ms per detection
- **Memory usage:** 200-400MB
- **CPU usage:** 15-30% (single core)

---

## Getting Help

1. Check `safedrive.log` for error messages
2. Verify you have latest dependencies: `pip install -r requirements.txt --upgrade`
3. Test individual modules: `python drowsiness_detection.py`
4. Review [API Documentation](API_DOCUMENTATION.md)
5. Check browser console for JavaScript errors (F12)
