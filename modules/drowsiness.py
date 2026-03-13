"""
Drowsiness Detection Module
Uses MediaPipe FaceMesh + EAR (Eye Aspect Ratio) and MAR (Mouth Aspect Ratio)
to detect drowsiness and yawning in real-time.
"""

import cv2
import numpy as np
import mediapipe as mp
from collections import deque

# MediaPipe landmark indices for eyes and mouth
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
MOUTH     = [61, 291, 39, 181, 0, 17, 269, 405]

EAR_THRESHOLD     = 0.25   # below this → eye closed
MAR_THRESHOLD     = 0.65   # above this → yawning
CONSEC_FRAMES     = 20     # frames eye must be closed to trigger alert
YAWN_CONSEC_FRAMES = 15

class DrowsinessDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.ear_history = deque(maxlen=30)
        self.blink_counter = 0
        self.yawn_counter  = 0
        self.total_blinks  = 0
        self.drowsy_frames = 0
        self.yawn_frames   = 0

    def _euclidean(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def _ear(self, landmarks, indices, w, h):
        pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices]
        A = self._euclidean(pts[1], pts[5])
        B = self._euclidean(pts[2], pts[4])
        C = self._euclidean(pts[0], pts[3])
        return (A + B) / (2.0 * C) if C != 0 else 0

    def _mar(self, landmarks, w, h):
        pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in MOUTH]
        A = self._euclidean(pts[1], pts[7])
        B = self._euclidean(pts[2], pts[6])
        C = self._euclidean(pts[3], pts[5])
        D = self._euclidean(pts[0], pts[4])
        return (A + B + C) / (2.0 * D) if D != 0 else 0

    def process_frame(self, frame):
        """
        Process a single BGR frame.
        Returns dict with detection results and annotated frame.
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        status = {
            "face_detected": False,
            "ear": 0.0,
            "mar": 0.0,
            "drowsy": False,
            "yawning": False,
            "blink_rate": 0,
            "score": 0   # 0-10 drowsiness sub-score
        }

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            status["face_detected"] = True

            left_ear  = self._ear(lm, LEFT_EYE,  w, h)
            right_ear = self._ear(lm, RIGHT_EYE, w, h)
            avg_ear   = (left_ear + right_ear) / 2.0
            mar       = self._mar(lm, w, h)

            status["ear"] = round(avg_ear, 3)
            status["mar"] = round(mar, 3)
            self.ear_history.append(avg_ear)

            # Drowsiness
            if avg_ear < EAR_THRESHOLD:
                self.drowsy_frames += 1
                if self.drowsy_frames >= CONSEC_FRAMES:
                    status["drowsy"] = True
            else:
                if self.drowsy_frames >= 2:
                    self.total_blinks += 1
                self.drowsy_frames = 0

            # Yawning
            if mar > MAR_THRESHOLD:
                self.yawn_frames += 1
                if self.yawn_frames >= YAWN_CONSEC_FRAMES:
                    status["yawning"] = True
            else:
                self.yawn_frames = 0

            # Sub-score (0-10)
            score = 0
            if status["drowsy"]:  score += 6
            if status["yawning"]: score += 4
            score += max(0, (EAR_THRESHOLD - avg_ear) * 20)
            status["score"] = min(10, round(score, 1))

            # Draw landmarks on frame
            self._draw_overlay(frame, lm, w, h, status)

        return status, frame

    def _draw_overlay(self, frame, lm, w, h, status):
        color = (0, 0, 255) if (status["drowsy"] or status["yawning"]) else (0, 255, 0)
        for idx in LEFT_EYE + RIGHT_EYE:
            cx, cy = int(lm[idx].x * w), int(lm[idx].y * h)
            cv2.circle(frame, (cx, cy), 2, color, -1)
        for idx in MOUTH:
            cx, cy = int(lm[idx].x * w), int(lm[idx].y * h)
            cv2.circle(frame, (cx, cy), 2, (255, 165, 0), -1)

        cv2.putText(frame, f"EAR: {status['ear']:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"MAR: {status['mar']:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
        if status["drowsy"]:
            cv2.putText(frame, "DROWSY!", (w//2-80, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        if status["yawning"]:
            cv2.putText(frame, "YAWNING!", (w//2-90, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
