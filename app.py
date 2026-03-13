"""
SafeDrive.ai — Flask + SocketIO Web Application
Real-time driver safety monitoring dashboard.
"""

import cv2
import base64
import threading
import time
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from modules import (
    DrowsinessDetector,
    EnvironmentDetector,
    ChildPresenceDetector,
    RiskEngine,
)

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "safedrive_secret_2024"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ── Detector instances ───────────────────────────────────────────────────────
drowsiness_det  = DrowsinessDetector()
environment_det = EnvironmentDetector()
child_det       = ChildPresenceDetector()
risk_engine     = RiskEngine()

# ── Shared state ─────────────────────────────────────────────────────────────
camera_active   = False
camera_thread   = None
current_state   = {
    "drowsy":      False,
    "yawning":     False,
    "stress":      "Normal",
    "visibility":  "Clear",
    "child_alert": False,
    "risk_score":  0.0,
    "risk_level":  "Low Risk",
    "risk_color":  "#27ae60",
    "ear":         0.0,
    "mar":         0.0,
    "logs":        [],
}
drive_logs = []
stress_score_cache = 0   # updated via REST endpoint


# ── Camera streaming thread ──────────────────────────────────────────────────
def camera_loop():
    global camera_active, current_state, drive_logs

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        socketio.emit("camera_error", {"msg": "Cannot open camera."})
        camera_active = False
        return

    while camera_active:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        # ── Run detectors ─────────────────────────────────────────────────
        d_status, frame = drowsiness_det.process_frame(frame)
        e_status, frame = environment_det.analyze_frame(frame)
        c_status, frame = child_det.detect(frame)

        # ── Risk score ────────────────────────────────────────────────────
        risk = risk_engine.update(
            drowsiness_score   = d_status.get("score", 0),
            stress_score       = stress_score_cache,
            environment_score  = e_status.get("score", 0),
            child_score        = c_status.get("score", 0),
        )

        # ── Update shared state ───────────────────────────────────────────
        current_state.update({
            "drowsy":     d_status["drowsy"],
            "yawning":    d_status["yawning"],
            "ear":        d_status["ear"],
            "mar":        d_status["mar"],
            "stress":     "Normal",   # updated via /api/stress_score
            "visibility": e_status["condition"],
            "child_alert":c_status["alert"],
            "risk_score": risk["smooth_score"],
            "risk_level": risk["level"],
            "risk_color": risk["color"],
        })

        # ── Drive log ─────────────────────────────────────────────────────
        if d_status["drowsy"] or d_status["yawning"] or c_status["alert"]:
            msg = []
            if d_status["drowsy"]:   msg.append("Drowsiness Detected")
            if d_status["yawning"]:  msg.append("Yawning Detected")
            if c_status["alert"]:    msg.append("Child in Vehicle!")
            log_entry = f"{time.strftime('%H:%M:%S')} — {', '.join(msg)}"
            drive_logs.insert(0, log_entry)
            drive_logs = drive_logs[:50]

        # ── Encode frame ──────────────────────────────────────────────────
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        socketio.emit("frame_update", {
            "image":       frame_b64,
            "state":       current_state,
            "alerts":      risk_engine.get_alerts(8),
            "logs":        drive_logs[:8],
        })

        time.sleep(0.05)   # ~20 fps

    cap.release()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/status")
def status():
    return jsonify(current_state)


@app.route("/api/stress_score", methods=["POST"])
def update_stress():
    """Frontend sends stress score (0-10) after mic analysis."""
    global stress_score_cache
    data = request.get_json(silent=True) or {}
    stress_score_cache = float(data.get("score", 0))
    return jsonify({"ok": True})


@app.route("/api/engine", methods=["POST"])
def toggle_engine():
    data = request.get_json(silent=True) or {}
    child_det.set_engine_state(data.get("on", True))
    return jsonify({"engine_on": child_det.engine_on})


@app.route("/api/alerts")
def alerts():
    return jsonify(risk_engine.get_alerts(20))


# ── SocketIO events ───────────────────────────────────────────────────────────
@socketio.on("start_camera")
def start_camera():
    global camera_active, camera_thread
    if not camera_active:
        camera_active = True
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        emit("camera_status", {"active": True})


@socketio.on("stop_camera")
def stop_camera():
    global camera_active
    camera_active = False
    emit("camera_status", {"active": False})


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SafeDrive.ai — Driver Safety Monitor")
    print("  URL: http://127.0.0.1:5000")
    print("=" * 55)
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
