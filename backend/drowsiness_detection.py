"""
SafeDrive.ai v3 — Module 1: Drowsiness & Yawning Detection
Run: python drowsiness_detection.py
EAR < 0.25 for 18 frames → DROWSY | MAR > 0.60 for 12 frames → YAWNING
"""
import cv2, numpy as np, logging, sys
from collections import deque
from typing import Dict, Tuple, List, Any

log = logging.getLogger("safedrive.drowsiness")

LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
MOUTH_IDX = [61, 291, 0, 17, 78, 308, 82, 312]
FACE_OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,
             397,365,379,378,400,377,152,148,176,149,150,136,
             172,58,132,93,234,127,162,21,54,103,67,109]

EAR_THRESH = 0.25
MAR_THRESH = 0.60
EAR_CONSEC = 18
MAR_CONSEC = 12


def _dist(a: Any, b: Any) -> float:
    return float(np.hypot(a.x - b.x, a.y - b.y))


def compute_ear(landmarks: List[Any], idx: List[int]) -> float:
    """EAR = (||p1-p5|| + ||p2-p4||) / (2 * ||p0-p3||)"""
    p = [landmarks[i] for i in idx]
    A, B, C = _dist(p[1], p[5]), _dist(p[2], p[4]), _dist(p[0], p[3])
    return (A + B) / (2.0 * C) if C > 0 else 0.0


def compute_mar(landmarks: List[Any]) -> float:
    """MAR = (A + B + C) / (2D) — high = yawning"""
    p = [landmarks[i] for i in MOUTH_IDX]
    A, B, C, D = _dist(p[2], p[3]), _dist(p[4], p[5]), _dist(p[6], p[7]), _dist(p[0], p[1])
    return (A + B + C) / (2.0 * D) if D > 0 else 0.0


class DrowsinessDetector:
    """Real-time EAR/MAR drowsiness & yawning detector."""

    def __init__(self, ear_thresh: float = EAR_THRESH, mar_thresh: float = MAR_THRESH) -> None:
        import mediapipe as mp
        if not hasattr(mp, "solutions"):
            raise RuntimeError(
                "Incompatible mediapipe import (missing 'solutions'). "
                f"Current Python: {sys.executable}. "
                "Activate project venv and run with ..\\.venv\\Scripts\\python.exe."
            )
        self.ear_thresh = ear_thresh
        self.mar_thresh = mar_thresh
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self._ear_frames = self._mar_frames = self._blinks = 0
        self.ear_history: deque = deque(maxlen=90)

    def process(self, bgr_frame: np.ndarray) -> Tuple[Dict[str, Any], np.ndarray]:
        h, w = bgr_frame.shape[:2]
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        out = self.face_mesh.process(rgb)
        res: Dict[str, Any] = dict(face_detected=False, ear=0.0, mar=0.0,
                                    drowsy=False, yawning=False, blinks=self._blinks, score=0.0)
        if not out.multi_face_landmarks:
            return res, bgr_frame
        lm = out.multi_face_landmarks[0].landmark
        res["face_detected"] = True
        ear = (compute_ear(lm, LEFT_EYE) + compute_ear(lm, RIGHT_EYE)) / 2.0
        mar = compute_mar(lm)
        res["ear"] = round(ear, 3)
        res["mar"] = round(mar, 3)
        self.ear_history.append(ear)
        if ear < self.ear_thresh:
            self._ear_frames += 1
        else:
            if self._ear_frames >= 2: self._blinks += 1
            self._ear_frames = 0
        res["drowsy"] = self._ear_frames >= EAR_CONSEC
        res["blinks"] = self._blinks
        if mar > self.mar_thresh: self._mar_frames += 1
        else: self._mar_frames = 0
        res["yawning"] = self._mar_frames >= MAR_CONSEC
        score = (7.0 if res["drowsy"] else 0.0) + (2.5 if res["yawning"] else 0.0)
        score += max(0.0, (self.ear_thresh - ear) * 22.0)
        res["score"] = round(min(10.0, score), 1)
        self._draw(bgr_frame, lm, w, h, res)
        return res, bgr_frame

    def _draw(self, frame, lm, w, h, r):
        def pt(i): return (int(lm[i].x * w), int(lm[i].y * h))
        ec = (0, 0, 255) if r["drowsy"] else (0, 230, 80)
        mc = (0, 80, 255) if r["yawning"] else (0, 165, 255)
        for i in LEFT_EYE + RIGHT_EYE: cv2.circle(frame, pt(i), 2, ec, -1)
        for i in MOUTH_IDX: cv2.circle(frame, pt(i), 2, mc, -1)
        cv2.polylines(frame, [np.array([pt(i) for i in FACE_OVAL], np.int32)], True, ec, 1)
        cv2.putText(frame, f"EAR:{r['ear']:.3f}", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.62, ec, 2)
        cv2.putText(frame, f"MAR:{r['mar']:.3f}", (8, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.62, mc, 2)
        cv2.putText(frame, f"Blinks:{r['blinks']}", (8, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (100,180,220), 1)
        if r["drowsy"]:
            cv2.rectangle(frame, (w//2-150, 16), (w//2+150, 58), (0,0,180), -1)
            cv2.putText(frame, "!! DROWSY — PULL OVER !!", (w//2-138, 46),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
        if r["yawning"]:
            cv2.putText(frame, "YAWNING DETECTED", (w//2-95, 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,120,255), 2)

    def release(self): self.face_mesh.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    det = DrowsinessDetector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): print("Cannot open camera"); exit(1)
    print("SafeDrive.ai v3 — Drowsiness Detection  (Q=quit)")
    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)
        res, frame = det.process(frame)
        s = "DROWSY" if res["drowsy"] else ("YAWNING" if res["yawning"] else "OK")
        print(f"\r  EAR={res['ear']:.3f}  MAR={res['mar']:.3f}  {s:8s}  Blinks={res['blinks']}  Score={res['score']:.1f}", end="")
        cv2.imshow("SafeDrive.ai — Drowsiness", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"): break
    cap.release(); cv2.destroyAllWindows(); det.release(); print()
