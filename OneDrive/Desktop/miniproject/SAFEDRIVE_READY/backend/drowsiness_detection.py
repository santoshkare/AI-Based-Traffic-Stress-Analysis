"""
SafeDrive.ai - Module 1: Drowsiness & Yawning Detection
=========================================================
Objective 1: Detect driver drowsiness and yawning using face analysis

Algorithm:
  EAR (Eye Aspect Ratio)   < 0.25 for 18 frames  → DROWSY
  MAR (Mouth Aspect Ratio) > 0.60 for 12 frames  → YAWNING

Run: python drowsiness_detection.py
"""

import cv2
import numpy as np
from collections import deque
from typing import Dict, Tuple, List, Any

# MediaPipe landmark indices
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
MOUTH_IDX = [61, 291, 0, 17, 78, 308, 82, 312]
FACE_OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,
             379,378,400,377,152,148,176,149,150,136,172,58,132,93,
             234,127,162,21,54,103,67,109]

EAR_THRESH  = 0.25
MAR_THRESH  = 0.60
EAR_CONSEC  = 18
MAR_CONSEC  = 12


def _dist(a: Any, b: Any) -> float:
    """Calculate Euclidean distance between two landmarks."""
    return float(np.hypot(a.x - b.x, a.y - b.y))


def compute_ear(landmarks: List[Any], idx: List[int]) -> float:
    """
    Compute Eye Aspect Ratio (EAR).
    
    EAR = (||p1-p5|| + ||p2-p4||) / (2 * ||p0-p3||)
    Low EAR indicates closed eyes.
    """
    p = [landmarks[i] for i in idx]
    A = _dist(p[1], p[5])
    B = _dist(p[2], p[4])
    C = _dist(p[0], p[3])
    return (A + B) / (2.0 * C) if C > 0 else 0.0


def compute_mar(landmarks: List[Any]) -> float:
    """
    Compute Mouth Aspect Ratio (MAR).
    
    High MAR indicates open mouth (yawning).
    """
    p = [landmarks[i] for i in MOUTH_IDX]
    A = _dist(p[2], p[3])
    B = _dist(p[4], p[5])
    C = _dist(p[6], p[7])
    D = _dist(p[0], p[1])
    return (A + B + C) / (2.0 * D) if D > 0 else 0.0


class DrowsinessDetector:
    """Detect drowsiness and yawning from facial landmarks."""
    
    def __init__(self) -> None:
        """Initialize the face mesh detector."""
        import mediapipe as mp
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._ear_frames: int = 0
        self._mar_frames: int = 0
        self._blinks: int = 0
        self.ear_history: deque = deque(maxlen=60)

    def process(self, bgr_frame: np.ndarray) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Process frame and detect drowsiness/yawning.
        
        Args:
            bgr_frame: Input video frame in BGR format
            
        Returns:
            Tuple of (detection_results, annotated_frame)
        """
        h, w = bgr_frame.shape[:2]
        rgb  = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        out  = self.face_mesh.process(rgb)

        res: Dict[str, Any] = dict(face_detected=False, ear=0.0, mar=0.0,
                   drowsy=False, yawning=False,
                   blinks=self._blinks, score=0.0)

        if out.multi_face_landmarks:
            lm = out.multi_face_landmarks[0].landmark
            res["face_detected"] = True

            ear = (compute_ear(lm, LEFT_EYE) + compute_ear(lm, RIGHT_EYE)) / 2.0
            mar = compute_mar(lm)
            res["ear"] = round(ear, 3)
            res["mar"] = round(mar, 3)
            self.ear_history.append(ear)

            # Drowsiness (EAR)
            if ear < EAR_THRESH:
                self._ear_frames += 1
            else:
                if self._ear_frames >= 2:
                    self._blinks += 1
                self._ear_frames = 0
            res["drowsy"] = self._ear_frames >= EAR_CONSEC
            res["blinks"] = self._blinks

            # Yawning (MAR)
            if mar > MAR_THRESH:
                self._mar_frames += 1
            else:
                self._mar_frames = 0
            res["yawning"] = self._mar_frames >= MAR_CONSEC

            # Sub-score 0-10
            score = (6.0 if res["drowsy"] else 0.0) + (3.0 if res["yawning"] else 0.0)
            score += max(0.0, (EAR_THRESH - ear) * 20.0)
            res["score"] = round(min(10.0, score), 1)

            self._draw(bgr_frame, lm, w, h, res)

        return res, bgr_frame

    def _draw(self, frame: np.ndarray, lm: List[Any], w: int, h: int, r: Dict[str, Any]) -> None:
        """Draw landmarks and annotations on frame."""
        def pt(i: int) -> Tuple[int, int]:
            return int(lm[i].x * w), int(lm[i].y * h)
        
        ec = (0, 0, 255) if r["drowsy"] else (0, 220, 80)
        mc = (0, 80, 255) if r["yawning"] else (0, 165, 255)
        for i in LEFT_EYE + RIGHT_EYE: cv2.circle(frame, pt(i), 2, ec, -1)
        for i in MOUTH_IDX:            cv2.circle(frame, pt(i), 2, mc, -1)
        cv2.polylines(frame, [np.array([pt(i) for i in FACE_OVAL], np.int32)], True, ec, 1)
        cv2.putText(frame, f"EAR:{r['ear']:.2f}", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ec, 2)
        cv2.putText(frame, f"MAR:{r['mar']:.2f}", (8, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mc, 2)
        if r["drowsy"]:
            cv2.putText(frame, "!! DROWSY !!", (w//2-110, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
        if r["yawning"]:
            cv2.putText(frame, "YAWNING", (w//2-75, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,120,255), 2)

    def release(self) -> None:
        """Release resources."""
        self.face_mesh.close()


if __name__ == "__main__":
    det = DrowsinessDetector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): print("Cannot open camera"); exit(1)
    print("SafeDrive.ai — Drowsiness Detection  (Q to quit)")
    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)
        res, frame = det.process(frame)
        s = "DROWSY" if res["drowsy"] else ("YAWNING" if res["yawning"] else "OK")
        print(f"\rEAR={res['ear']:.3f}  MAR={res['mar']:.3f}  Status={s:8s}  Blinks={res['blinks']}  Score={res['score']}", end="")
        cv2.imshow("SafeDrive.ai - Drowsiness", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release(); cv2.destroyAllWindows(); det.release()
