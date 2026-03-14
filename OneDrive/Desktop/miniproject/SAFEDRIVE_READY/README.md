# 🚗 SafeDrive.ai

### Real-Time Driver Safety Monitoring System

> _Accident Prevention · Before It Happens_

---

## ✅ All 8 Objectives — Working

| #   | Objective               | File                      | Method                                  |
| --- | ----------------------- | ------------------------- | --------------------------------------- |
| 1   | Drowsiness & Yawning    | `drowsiness_detection.py` | EAR < 0.25 → Drowsy · MAR > 0.60 → Yawn |
| 2   | Emotion Detection       | `emotion_detection.py`    | 6-class geometry from 468 landmarks     |
| 3   | Stress via Voice        | `stress_detection.py`     | MFCC + Pitch + RMS + ZCR → RandomForest |
| 4   | Visibility Detection    | `visibility_detection.py` | Brightness / Contrast / Laplacian       |
| 5   | Child in Locked Vehicle | `visibility_detection.py` | Frame differencing when engine OFF      |
| 6   | Real-time Risk Score    | `risk_engine.py`          | Weighted 0–10 with 30-frame smoothing   |
| 7   | Web Dashboard + Alerts  | `frontend/index.html`     | Live camera, gauge, logs, alerts        |
| 8   | Deployment              | `backend/app.py`          | Flask server OR direct HTML             |

---

## 📁 Structure

```
SAFEDRIVE_FINAL/
├── frontend/
│   └── index.html              ← Open in Chrome (login + full dashboard)
├── backend/
│   ├── app.py                  ← Flask server
│   ├── drowsiness_detection.py ← Obj 1
│   ├── emotion_detection.py    ← Obj 2
│   ├── stress_detection.py     ← Obj 3
│   ├── visibility_detection.py ← Obj 4 & 5
│   ├── risk_engine.py          ← Obj 6
│   └── run_all.py              ← All modules together
├── docs/
│   ├── PROJECT_REPORT.md       ← Detailed project overview
│   ├── VIVA_NOTES.md           ← Interview preparation
│   ├── API_DOCUMENTATION.md    ← REST API reference (NEW)
│   ├── DEPLOYMENT.md           ← Setup & deployment guide (NEW)
│   └── CONFIGURATION.md        ← Configuration options (NEW)
├── requirements.txt            ← Python dependencies (pinned versions)
├── .gitignore                  ← Git ignore rules (NEW)
├── start.bat                   ← Windows launcher
└── README.md                   ← This file
```

---

## 🚀 Quick Start

### Option 1: Browser Only (No Installation)

```
1. Open: frontend/index.html in Google Chrome or Edge
2. Login or click "Continue as Guest"
3. Click: ▶ Start → Allow camera & microphone
```

> **✨ Best for:** Quick testing, no setup required

### Option 2: Flask Web Server (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
cd backend
python app.py

# 3. Open http://localhost:5000 in Chrome
```

> **✨ Best for:** Full features, multi-user, deployment

### Option 3: Python Window (Direct Processing)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run detection
cd backend
python run_all.py

# Controls: E = engine ON/OFF | R = reset | Q = quit
```

> **✨ Best for:** Debugging, module testing

### Option 4: Windows Batch (Easiest)

Double-click `start.bat` to automatically install and run.

---

## 🔐 Login Credentials

| Email                | Password   | Access              |
| -------------------- | ---------- | ------------------- |
| `admin@safedrive.ai` | `admin123` | Full admin access   |
| `demo@test.com`      | `demo1234` | Demo driver account |
| Guest                | (none)     | Limited guest mode  |

> **Security Note:** Change these credentials before production deployment. See [CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 📋 Test Individual Modules

```bash
cd backend

# Test drowsiness & yawning detection
python drowsiness_detection.py
# Shows: EAR, MAR, blinks, drowsiness alerts

# Test emotion detection
python emotion_detection.py
# Shows: Happy, Sad, Angry, Surprised, Fearful, Neutral percentages

# Test stress detection (console demo)
python stress_detection.py
# Simulates voice stress analysis with audio features

# Test visibility detection
python visibility_detection.py
# Shows: Brightness, contrast, and child detection when engine OFF

# Test risk engine (console simulation)
python risk_engine.py
# Simulates risk scoring with multiple factors
```

---

## 📡 API Documentation

Full REST API documentation available in [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

### Quick API Examples

```bash
# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"demo1234"}' \
  -c cookies.txt

# Log event
curl -X POST http://localhost:5000/api/log_event \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type":"drowsiness","score":7.5}'

# Get stats
curl http://localhost:5000/api/stats -b cookies.txt
```

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete endpoint reference.

---

## 🛠️ Configuration & Deployment

### Setup & Installation

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:

- Detailed installation instructions
- Multi-method deployment options
- Docker support
- Production checklist
- Troubleshooting guide

### Customization

See [CONFIGURATION.md](docs/CONFIGURATION.md) for:

- Detection thresholds tuning
- Risk score weights adjustment
- Credential management
- Performance optimization
- Environment variables
- Integration examples

---

## 🔧 Tech Stack

| Component       | Technology                         |
| --------------- | ---------------------------------- |
| Face Detection  | MediaPipe FaceMesh (468 landmarks) |
| Computer Vision | OpenCV                             |
| Audio Analysis  | Librosa (MFCC, pYIN, RMS, ZCR)     |
| ML Classifier   | scikit-learn RandomForest          |
| Web Framework   | Flask                              |
| Frontend        | HTML5 + CSS3 + Vanilla JS          |

---

## 📐 Key Formulas

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)
      EAR < 0.25 for 18 frames → DROWSY

MAR = (A + B + C) / (2D)
      MAR > 0.60 for 12 frames → YAWNING

Risk = (Drowsiness×0.35) + (Stress×0.25) + (Environment×0.20) + (Child×0.20)
       Smoothed over 30-frame rolling window
       0-3 = Low  ·  3-6 = Medium  ·  6-10 = High
```

---

## 🛠 Tech Stack

| Component       | Technology                         |
| --------------- | ---------------------------------- |
| Face Detection  | MediaPipe FaceMesh (468 landmarks) |
| Computer Vision | OpenCV                             |
| Audio Analysis  | Librosa (MFCC, pYIN, RMS, ZCR)     |
| ML Classifier   | scikit-learn RandomForest          |
| Web Framework   | Flask                              |
| Frontend        | HTML5 + CSS3 + Vanilla JS          |

---

_SafeDrive.ai — Mini Project · CSE Department_
