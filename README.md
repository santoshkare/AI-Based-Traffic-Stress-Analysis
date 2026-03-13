# SafeDrive.ai 🚗

**Real-Time Driver Safety Monitoring System**

A software-based, low-cost safety system that detects driver fatigue, stress, and environmental hazards before accidents happen.

---

## 📁 Project Structure

```
safedrive_ai/
├── app.py                  ← Flask + SocketIO web server
├── demo.py                 ← Terminal demo (no camera needed)
├── requirements.txt
├── modules/
│   ├── drowsiness.py       ← EAR / MAR face analysis
│   ├── stress.py           ← Voice-based stress classification
│   ├── environment.py      ← Fog / low-light / blur detection
│   ├── child_presence.py   ← Motion detection for locked vehicle
│   └── risk_engine.py      ← Combined risk score (0–10)
└── templates/
    └── dashboard.html      ← Real-time web dashboard
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the demo (no camera needed)

```bash
python demo.py
```

### 3. Run the full web dashboard

```bash
python app.py
```

Then open: **http://127.0.0.1:5000**

Click **"Start Camera"** to begin live detection.

---

## 🧠 Modules

### 👁 Drowsiness Detection (`modules/drowsiness.py`)
- Uses **MediaPipe FaceMesh** + **OpenCV**
- Computes **Eye Aspect Ratio (EAR)** — if EAR < 0.25 for 20 frames → Drowsy
- Computes **Mouth Aspect Ratio (MAR)** — if MAR > 0.65 for 15 frames → Yawning
- Sub-score: **0–10**

### 🎤 Stress Detection (`modules/stress.py`)
- Extracts **MFCC, Pitch, Energy, ZCR** features from microphone input
- Classifies into: **Normal | Mild Stress | High Stress**
- Uses **Librosa** + **Scikit-learn** RandomForest
- Sub-score: 0 / 4 / 8

### 🌫 Environment Detection (`modules/environment.py`)
- **No sensors** — pure camera/image processing
- Fog → low image contrast (std dev)
- Low-light → low mean brightness
- Blur → Laplacian variance
- Output: **Clear | Low-Light | Fog | Blurry**

### 👶 Child Presence (`modules/child_presence.py`)
- Motion detection using frame differencing
- Triggers alert when **engine is OFF** + motion detected
- Simulates child-left-in-vehicle scenario

### ⚡ Risk Engine (`modules/risk_engine.py`)
- Weighted combination of all sub-scores:
  - Drowsiness 35% · Stress 25% · Environment 20% · Child 20%
- Smoothed over 30-frame rolling window
- Levels: **Low (0–3) | Medium (3–6) | High (6–10)**

---

## 🖥 Dashboard Features

- Live camera feed with facial landmark overlay
- Real-time risk score gauge (0–10)
- Module sub-score bars
- Status indicators (green / yellow / red)
- Driving log + recent alerts panel
- Engine ON/OFF toggle (for child presence demo)

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Face Analysis | MediaPipe FaceMesh, OpenCV |
| Stress Analysis | Librosa, Scikit-learn |
| Web Framework | Flask, Flask-SocketIO |
| Frontend | HTML5, CSS3, Socket.IO |
| Language | Python 3.9+ |

---

## 📋 Requirements

- Python 3.9 or later
- Webcam (for live mode)
- Microphone (for stress detection)

---

## 🎓 Project Objectives (Mini Project)

1. ✅ Detect drowsiness and yawning using face analysis (EAR/MAR)  
2. ✅ Identify driver state in real time  
3. ✅ Analyze stress using voice signals (MFCC features)  
4. ✅ Detect low-visibility conditions via camera  
5. ✅ Child presence detection in locked vehicle  
6. ✅ Generate real-time risk score (0–10)  
7. ✅ Display alerts on web dashboard  
8. ✅ Deployable Flask application  

---

*Goal: Accident prevention before it happens.*
