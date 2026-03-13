"""
Child Presence Detection in Locked Vehicle
Uses motion detection + temperature simulation to flag child left in car.
In a real system, this would use an IR sensor or secondary camera.
Here we use frame differencing as a software-only demo.
"""

import cv2
import numpy as np
from collections import deque


class ChildPresenceDetector:
    def __init__(self):
        self.prev_frame   = None
        self.motion_history = deque(maxlen=50)
        self.engine_on    = True   # toggled externally

    def set_engine_state(self, on: bool):
        self.engine_on = on

    def detect(self, frame):
        """
        Detect if a child/person is present while engine is off.
        Returns result dict.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        motion_detected = False
        motion_score    = 0

        if self.prev_frame is not None:
            delta = cv2.absdiff(self.prev_frame, gray)
            thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(thresh.copy(),
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                if cv2.contourArea(c) > 1500:
                    motion_detected = True
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    motion_score += cv2.contourArea(c)

        self.prev_frame = gray.copy()
        self.motion_history.append(1 if motion_detected else 0)

        # Alert only when engine is OFF and motion detected
        alert = (not self.engine_on) and motion_detected
        recent_motion_pct = sum(self.motion_history) / max(1, len(self.motion_history))

        if alert:
            cv2.putText(frame, "⚠ CHILD IN VEHICLE!", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        return {
            "motion_detected": motion_detected,
            "engine_on":       self.engine_on,
            "alert":           alert,
            "recent_motion":   round(recent_motion_pct, 2),
            "score":           8 if alert else 0
        }, frame
