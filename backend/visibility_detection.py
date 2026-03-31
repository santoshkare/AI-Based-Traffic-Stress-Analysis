"""
SafeDrive.ai - Module 4 & 5: Visibility + Child Presence Detection
===================================================================
Objective 4: Detect low-visibility conditions via camera (no sensors)
Objective 5: Child Presence Detection in Locked Vehicle

Visibility:
  Fog       → low contrast  (std dev of gray < 25)
  Low-Light → low brightness (mean gray < 40)
  Blurry    → low Laplacian  (var < 80)
  Clear     → default

Child Presence:
  Frame differencing when engine is OFF → motion → ALERT

Run: python visibility_detection.py
"""

import cv2
import numpy as np
from collections import deque

BRIGHT_THRESH   = 40
CONTRAST_THRESH = 25
BLUR_THRESH     = 80
MOTION_THRESH   = 8.0
MOTION_MIN_AREA = 1200

VIS_LABELS = {0: "Clear", 1: "Low-Light", 2: "Fog", 3: "Blurry"}
VIS_SCORES = {0: 0, 1: 4, 2: 5, 3: 3}
VIS_COLORS = {0:(0,220,80), 1:(0,165,255), 2:(190,190,190), 3:(180,0,180)}


class VisibilityDetector:
    def analyze(self, bgr_frame):
        gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        br   = float(np.mean(gray))
        con  = float(np.std(gray))
        blr  = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        if   br  < BRIGHT_THRESH:   cid = 1
        elif con < CONTRAST_THRESH: cid = 2
        elif blr < BLUR_THRESH:     cid = 3
        else:                       cid = 0

        res = {"condition": VIS_LABELS[cid], "cid": cid,
               "brightness": round(br, 1), "contrast": round(con, 1),
               "blur_var": round(blr, 1), "score": VIS_SCORES[cid]}

        col = VIS_COLORS[cid]
        cv2.putText(bgr_frame, f"Visibility: {res['condition']}",
                    (8, bgr_frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 2)
        if cid == 2:   # fog tint
            fog = bgr_frame.copy()
            cv2.rectangle(fog, (0, 0), (bgr_frame.shape[1], bgr_frame.shape[0]),
                          (180, 185, 190), -1)
            cv2.addWeighted(fog, 0.22, bgr_frame, 0.78, 0, bgr_frame)
        return res, bgr_frame


class ChildPresenceDetector:
    def __init__(self):
        self.engine_on  = True
        self.prev_gray  = None
        self.motion_buf = deque(maxlen=30)

    def set_engine(self, on):
        self.engine_on = on
        if on: self.prev_gray = None

    def detect(self, bgr_frame):
        gray = cv2.GaussianBlur(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        motion = False

        if self.prev_gray is not None:
            diff   = cv2.absdiff(self.prev_gray, gray)
            motion = float(np.mean(diff)) > MOTION_THRESH
            thr    = cv2.dilate(cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1], None, iterations=2)
            cnts, _ = cv2.findContours(thr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                if cv2.contourArea(c) > MOTION_MIN_AREA:
                    x, y, bw, bh = cv2.boundingRect(c)
                    cv2.rectangle(bgr_frame, (x, y), (x+bw, y+bh), (0, 0, 255), 2)

        self.prev_gray = gray.copy()
        self.motion_buf.append(1 if motion else 0)
        alert = (not self.engine_on) and motion
        res   = {"motion": motion, "alert": alert,
                 "engine_on": self.engine_on,
                 "recent_pct": round(sum(self.motion_buf)/max(1,len(self.motion_buf)), 2),
                 "score": 9 if alert else 0}

        if alert:
            h, w = bgr_frame.shape[:2]
            ov = bgr_frame.copy()
            cv2.rectangle(ov, (0,0), (w,h), (0,0,200), -1)
            cv2.addWeighted(ov, 0.18, bgr_frame, 0.82, 0, bgr_frame)
            cv2.putText(bgr_frame, "!! CHILD IN VEHICLE !!",
                        (w//2 - 165, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0,0,255), 3)
        return res, bgr_frame


if __name__ == "__main__":
    vis   = VisibilityDetector()
    child = ChildPresenceDetector()
    cap   = cv2.VideoCapture(0)
    if not cap.isOpened(): print("Cannot open camera"); exit(1)
    print("SafeDrive.ai — Visibility + Child Detection")
    print("  E = toggle engine  |  Q = quit")
    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)
        vr, frame = vis.analyze(frame)
        cr, frame = child.detect(frame)
        print(f"\rVis:{vr['condition']:10s}  Engine:{'ON' if child.engine_on else 'OFF'}  Child:{cr['alert']}", end="")
        cv2.imshow("SafeDrive.ai - Visibility & Child", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('e'):
            child.set_engine(not child.engine_on)
            print(f"\nEngine: {'ON' if child.engine_on else 'OFF'}")
    cap.release(); cv2.destroyAllWindows()
