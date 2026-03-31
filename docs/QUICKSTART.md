# SafeDrive.ai - Quick Reference Guide

## 🚀 Getting Started (Choose One)

### Option A: Browser Only (Instant)

```
1. Open: frontend/index.html
2. Login: demo@test.com / demo1234
3. Click Start → Allow camera & mic
```

### Option B: Flask Server (Recommended)

```bash
pip install -r requirements.txt
cd backend
python app.py
# Visit: http://localhost:5000
```

### Option C: Python Direct (Testing)

```bash
pip install -r requirements.txt
cd backend
python run_all.py
# Press: E = Engine Toggle | Q = Quit
```

### Option D: Windows Batch (Easiest)

```
Double-click: start.bat
```

---

## 📖 Documentation Map

| Document                                          | Purpose               | Read if...                |
| ------------------------------------------------- | --------------------- | ------------------------- |
| [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | REST API reference    | Building integrations     |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md)               | Setup & deployment    | Deploying to production   |
| [CONFIGURATION.md](docs/CONFIGURATION.md)         | Configuration options | Customizing system        |
| [IMPROVEMENTS.md](IMPROVEMENTS.md)                | What's new in v2.0    | Reviewing changes         |
| [PROJECT_REPORT.md](docs/PROJECT_REPORT.md)       | Technical details     | Learning about project    |
| [VIVA_NOTES.md](docs/VIVA_NOTES.md)               | Interview prep        | Studying for presentation |

---

## 🔑 Default Accounts

```
Email: demo@test.com
Password: demo1234

Email: admin@safedrive.ai
Password: admin123

Or: Click "Continue as Guest"
```

---

## 🧪 Test Individual Modules

```bash
cd backend

# Drowsiness detection (webcam)
python drowsiness_detection.py

# Emotion detection (webcam)
python emotion_detection.py

# Stress detection (console)
python stress_detection.py

# Visibility detection (webcam)
python visibility_detection.py

# Risk engine (console)
python risk_engine.py
```

---

## 📡 Quick API Examples

### Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"demo1234"}' \
  -c cookies.txt
```

### Log Event

```bash
curl -X POST http://localhost:5000/api/log_event \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type":"drowsiness","score":7.5}'
```

### Get Stats

```bash
curl http://localhost:5000/api/stats -b cookies.txt
```

### Logout

```bash
curl -X POST http://localhost:5000/api/logout -b cookies.txt
```

_See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete reference_

---

## ⚙️ Quick Configuration

### Change Detection Sensitivity

**File:** `backend/drowsiness_detection.py`

```python
EAR_THRESH = 0.25    # Lower = more sensitive (0.20 for night mode)
MAR_THRESH = 0.60    # Higher = more sensitive
EAR_CONSEC = 18      # Frames until trigger (lower = faster)
```

### Adjust Risk Weights

**File:** `backend/risk_engine.py`

```python
WEIGHTS = {
    "drowsiness": 0.35,   # Increase for drowsy focus
    "stress": 0.25,       # Increase for stress focus
    "environment": 0.20,  # Visibility importance
    "child": 0.20        # Child detection importance
}
```

### Change Appearance Colors

**File:** `frontend/index.html` (CSS section)

```css
:root {
  --bg: #080c14; /* Background */
  --red: #e74c3c; /* Alert color */
  --green: #22c55e; /* Safe color */
  --yellow: #f0a500; /* Warning color */
}
```

---

## 🔐 Security Checklist

- [ ] Change default passwords (see [CONFIGURATION.md](docs/CONFIGURATION.md))
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Whitelist CORS origins
- [ ] Review `safedrive.log` regularly
- [ ] Backup event data regularly
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting in production

See [DEPLOYMENT.md](docs/DEPLOYMENT.md#production-deployment) for full checklist.

---

## 🐛 Troubleshooting

### "Cannot open camera"

- Another app is using camera
- Check browser permissions
- Try different browser
- Allow camera access in Settings

### "Port 5000 in use"

```bash
# Use different port in app.py or:
python -c "
from app import app
app.run(port=5001)
"
```

### "MediaPipe not found"

```bash
pip install --upgrade mediapipe
```

### "Microphone not working"

- Grant microphone permission
- Check browser sound settings
- Try different browser (Chrome recommended)

_See [DEPLOYMENT.md](docs/DEPLOYMENT.md#troubleshooting) for more solutions_

---

## 📊 System Performance

| Metric       | Value          |
| ------------ | -------------- |
| FPS          | 20-30 (1080p)  |
| Latency      | 50-100ms       |
| Memory       | 200-400MB      |
| CPU          | 15-30%         |
| Max Sessions | Limited by RAM |

---

## 🔄 Key Features

### Detection Modules

- **Drowsiness:** Eye Aspect Ratio (EAR) < 0.25
- **Yawning:** Mouth Aspect Ratio (MAR) > 0.60
- **Emotions:** 6 emotions from 468 facial landmarks
- **Stress:** Voice analysis (MFCC, pitch, RMS)
- **Visibility:** Brightness, contrast, sharpness
- **Child Detection:** Frame differencing when engine off

### Risk Scoring

- Real-time weighted score (0-10)
- 30-frame rolling average smoothing
- Color-coded alerts:
  - 🟢 Green (0-3) = Low Risk
  - 🟡 Yellow (3-6) = Medium Risk
  - 🔴 Red (6-10) = High Risk

### Dashboard

- Live camera feed with overlays
- Risk gauge and history
- Event logs
- Emotion analysis
- Driver metrics
- Alert notifications

---

## 📁 Important Files

```
SafeDrive/
├── frontend/index.html           Web interface
├── backend/app.py                Flask server
├── backend/drowsiness_detection.py
├── backend/emotion_detection.py
├── backend/stress_detection.py
├── backend/visibility_detection.py
├── backend/risk_engine.py
├── backend/run_all.py            All modules
├── requirements.txt              Dependencies (pinned)
├── .gitignore                   Git rules
├── README.md                     Main guide
└── docs/
    ├── API_DOCUMENTATION.md     API reference
    ├── DEPLOYMENT.md            Setup guide
    ├── CONFIGURATION.md         Config options
    ├── IMPROVEMENTS.md          v2.0 updates
    ├── PROJECT_REPORT.md        Technical details
    └── VIVA_NOTES.md            Interview prep
```

---

## 💻 System Requirements

- **OS:** Windows, Mac, Linux
- **Python:** 3.8+
- **Browser:** Chrome, Edge (Firefox for basic use)
- **Hardware:** Webcam, Microphone
- **Memory:** 512MB minimum, 1GB+ recommended
- **Internet:** Not required (local operation)

---

## 🚀 Upgrade Notes (v1.0 → v2.0)

**New in v2.0:**

- ✅ Logging system (safedrive.log)
- ✅ Rate limiting (prevent brute force)
- ✅ Input validation & sanitization
- ✅ Type hints in Python code
- ✅ 3 comprehensive documentation files
- ✅ Pinned dependency versions
- ✅ .gitignore file
- ✅ Security improvements
- ✅ Better error messages
- ✅ Production deployment guide

**Backward compatible:** Yes, all existing functionality works

---

## 📞 Getting Help

**Step 1:** Check relevant documentation file  
**Step 2:** Review logs: `tail -f safedrive.log`  
**Step 3:** Test module: `python drowsiness_detection.py`  
**Step 4:** Check browser console: Press F12  
**Step 5:** Verify configuration: [CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 🎯 Common Tasks

### Task: Deploy to Production

→ See [DEPLOYMENT.md](docs/DEPLOYMENT.md#production-deployment)

### Task: Customize Risk Weights

→ See [CONFIGURATION.md](docs/CONFIGURATION.md#risk-engine-configuration)

### Task: Integrate with Mobile App

→ See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

### Task: Reduce CPU Usage

→ See [CONFIGURATION.md](docs/CONFIGURATION.md#performance-tuning)

### Task: Change Login Credentials

→ See [CONFIGURATION.md](docs/CONFIGURATION.md#credential-management)

### Task: Add Custom Detection

→ See [CONFIGURATION.md](docs/CONFIGURATION.md#integration-configuration)

---

## 📈 Metrics to Monitor

In `safedrive.log`, watch for:

- Login failures (rapid attempts = attack)
- API errors (configuration issues)
- Detection accuracy (threshold validation)
- Performance metrics (FPS, latency)

---

## 🔗 External Resources

- [MediaPipe Documentation](https://developers.google.com/mediapipe)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [scikit-learn Documentation](https://scikit-learn.org/)

---

**Quick Links:**

- 🚀 [Deployment Guide](docs/DEPLOYMENT.md)
- ⚙️ [Configuration Guide](docs/CONFIGURATION.md)
- 📡 [API Reference](docs/API_DOCUMENTATION.md)
- 📊 [Improvements Summary](IMPROVEMENTS.md)

---

**Version:** 2.0 | **Status:** Production-Ready ✅ | **Last Updated:** March 2026
