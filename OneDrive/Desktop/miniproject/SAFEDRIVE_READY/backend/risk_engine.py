"""
SafeDrive.ai - Module 6: Real-Time Risk Score Engine
=====================================================
Objective 6: Generate a real-time risk score (0-10)

Formula:  Risk = D×0.35 + S×0.25 + E×0.20 + C×0.20
Smoothed: 30-frame rolling average

Risk Levels:
  0.0-3.0  → Low Risk    🟢
  3.0-6.0  → Medium Risk 🟡
  6.0-10.0 → High Risk   🔴

Run: python risk_engine.py
"""

import time
from collections import deque
from typing import Dict, Tuple, List, Any

WEIGHTS: Dict[str, float] = {
    "drowsiness": 0.35,
    "stress": 0.25,
    "environment": 0.20,
    "child": 0.20
}

LEVELS: List[Tuple[float, float, str, str, str]] = [
    (0.0, 3.0,  "Low Risk",    "#22c55e", "\033[92m"),
    (3.0, 6.0,  "Medium Risk", "#f0a500", "\033[93m"),
    (6.0, 10.1, "High Risk",   "#e74c3c", "\033[91m"),
]


def get_level(score: float) -> Tuple[str, str]:
    """
    Get risk level label and color for a given score.
    
    Args:
        score: Risk score 0-10
        
    Returns:
        Tuple of (level_label, color_hex)
    """
    for lo, hi, label, color, _ in LEVELS:
        if lo <= score < hi:
            return label, color
    return "High Risk", "#e74c3c"


class RiskEngine:
    """Real-time risk scoring engine with smoothing and alerts."""
    
    def __init__(self, window: int = 30) -> None:
        """
        Initialize the risk engine.
        
        Args:
            window: Size of rolling average window (frames)
        """
        self.history: deque = deque(maxlen=window)
        self.alerts: deque = deque(maxlen=200)
        self.sub_last: Dict[str, float] = {}

    def update(self, drowsiness: float = 0.0, stress: float = 0.0,
               environment: float = 0.0, child: float = 0.0) -> Dict[str, Any]:
        """
        Update risk score with latest sensor readings.
        
        Args:
            drowsiness: Drowsiness level (0-10)
            stress: Stress level (0-10)
            environment: Environmental risk (0-10)
            child: Child detection risk (0-10)
            
        Returns:
            Dictionary containing risk metrics and status
        """
        # Calculate weighted raw score
        raw = (drowsiness  * WEIGHTS["drowsiness"]  +
               stress      * WEIGHTS["stress"]       +
               environment * WEIGHTS["environment"]  +
               child       * WEIGHTS["child"])
        raw = min(10.0, max(0.0, raw))
        self.history.append(raw)
        smooth = sum(self.history) / len(self.history)
        label, color = get_level(smooth)

        self.sub_last = dict(
            drowsiness=round(drowsiness, 1),
            stress=round(stress, 1),
            environment=round(environment, 1),
            child=round(child, 1)
        )

        res: Dict[str, Any] = {
            "raw": round(raw, 2),
            "score": round(smooth, 2),
            "level": label,
            "color": color,
            "sub": dict(self.sub_last),
            "timestamp": time.strftime("%H:%M:%S")
        }

        # Generate alerts for high risk levels
        if smooth >= 6.0:
            self._alert("⚠ HIGH RISK DETECTED", smooth)
        elif smooth >= 3.0:
            self._alert("⚡ Medium Risk", smooth)
            
        return res

    def _alert(self, msg: str, score: float) -> None:
        """
        Log an alert event.
        
        Args:
            msg: Alert message
            score: Associated risk score
        """
        self.alerts.appendleft({
            "time": time.strftime("%H:%M:%S"),
            "message": msg,
            "score": round(score, 1)
        })

    def get_alerts(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get most recent N alerts."""
        return list(self.alerts)[:n]
    
    def reset(self) -> None:
        """Reset history and alerts."""
        self.history.clear()
        self.alerts.clear()


if __name__ == "__main__":
    import random
    import sys
    
    engine = RiskEngine()
    print("SafeDrive.ai — Risk Engine Demo  (Ctrl+C to quit)\n")
    t = 0
    try:
        while True:
            d = max(0, min(10, random.gauss(3 if t%25<8 else 1, 1.5)))
            s = max(0, min(10, 8 if t%40<10 else random.gauss(1, 0.8)))
            e = max(0, min(10, random.gauss(1, 0.5)))
            c = 9 if (t%60>50 and t%2==0) else 0
            res = engine.update(d, s, e, c)
            bar = "█"*int(res["score"]*4) + "░"*(40-int(res["score"]*4))
            ansi = next((col for lo,hi,_,__,col in LEVELS if lo<=res["score"]<hi), LEVELS[-1][4])
            sys.stdout.write(f"\r[{bar}] {ansi}{res['score']:4.1f}/10  {res['level']:12s}\033[0m  D={d:.1f} S={s:.1f}")
            sys.stdout.flush()
            time.sleep(0.25)
            t += 1
    except KeyboardInterrupt:
        print(f"\n\nEnded.  Alerts: {len(engine.alerts)}")
