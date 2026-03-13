"""
Real-Time Risk Score Engine
Combines outputs from all detection modules into a single risk score (0-10).
"""

from collections import deque
import time


WEIGHTS = {
    "drowsiness":   0.35,
    "stress":       0.25,
    "environment":  0.20,
    "child":        0.20,
}

RISK_LEVELS = {
    (0.0, 3.0):  ("Low Risk",    "#27ae60"),
    (3.0, 6.0):  ("Medium Risk", "#f39c12"),
    (6.0, 10.1): ("High Risk",   "#e74c3c"),
}


def get_risk_level(score):
    for (lo, hi), (label, color) in RISK_LEVELS.items():
        if lo <= score < hi:
            return label, color
    return "High Risk", "#e74c3c"


class RiskEngine:
    def __init__(self, history_len=30):
        self.history  = deque(maxlen=history_len)
        self.alerts   = deque(maxlen=100)
        self.last_scores = {}

    def update(self, drowsiness_score=0, stress_score=0,
               environment_score=0, child_score=0):
        """
        Each sub-score is 0-10.
        Returns combined risk score dict.
        """
        weighted = (
            drowsiness_score   * WEIGHTS["drowsiness"]  +
            stress_score       * WEIGHTS["stress"]       +
            environment_score  * WEIGHTS["environment"]  +
            child_score        * WEIGHTS["child"]
        )
        combined = round(min(10.0, weighted), 2)
        self.history.append(combined)
        smoothed = round(sum(self.history) / len(self.history), 2)

        level, color = get_risk_level(smoothed)

        self.last_scores = {
            "drowsiness":  drowsiness_score,
            "stress":      stress_score,
            "environment": environment_score,
            "child":       child_score,
        }

        result = {
            "raw_score":     combined,
            "smooth_score":  smoothed,
            "level":         level,
            "color":         color,
            "sub_scores":    self.last_scores,
            "timestamp":     time.strftime("%H:%M:%S")
        }

        # Log alerts
        if smoothed >= 6.0:
            self._log_alert("⚠ High Risk Detected", smoothed)
        elif smoothed >= 3.0:
            self._log_alert("⚡ Medium Risk", smoothed)

        return result

    def _log_alert(self, message, score):
        self.alerts.appendleft({
            "time":    time.strftime("%H:%M:%S"),
            "message": message,
            "score":   score
        })

    def get_alerts(self, n=10):
        return list(self.alerts)[:n]
