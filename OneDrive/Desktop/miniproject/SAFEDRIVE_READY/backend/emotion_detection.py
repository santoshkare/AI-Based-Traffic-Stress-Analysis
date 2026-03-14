"""
SafeDrive.ai - Module 2: Real-Time Emotion Detection
=====================================================
Objective 2: Identify driver emotions in real time

Detects: Happy · Sad · Angry · Surprised · Fear · Neutral
Method:  Geometric facial ratios from 468 MediaPipe landmarks

Run: python emotion_detection.py
"""

import cv2
import numpy as np

EMOTIONS  = ["Happy", "Sad", "Angry", "Surprised", "Fear", "Neutral"]
ALPHA     = 0.25   # EMA smoothing factor
COLORS    = {
    "Happy":     (0, 220, 80),
    "Sad":       (220, 100, 60),
    "Angry":     (0, 0, 220),
    "Surprised": (0, 180, 255),
    "Fear":      (120, 0, 220),
    "Neutral":   (120, 140, 160),
}


def _d(a, b): return np.hypot(a.x - b.x, a.y - b.y)
def _c(v): return max(0.0, min(1.0, v))


class EmotionDetector:
    def __init__(self):
        import mediapipe as mp
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.smoothed = {e: 0.0 for e in EMOTIONS}

    def process(self, bgr_frame):
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        out = self.face_mesh.process(rgb)
        res = dict(face_detected=False,
                   emotions={e: 0.0 for e in EMOTIONS},
                   dominant="Neutral", score=0.0)

        if out.multi_face_landmarks:
            lm  = out.multi_face_landmarks[0].landmark
            raw = self._estimate(lm)
            res["face_detected"] = True

            for k in EMOTIONS:
                self.smoothed[k] = ALPHA * raw[k] + (1 - ALPHA) * self.smoothed[k]

            total = sum(self.smoothed.values()) or 1.0
            norm  = {k: v / total for k, v in self.smoothed.items()}
            res["emotions"] = {k: round(v, 3) for k, v in norm.items()}
            res["dominant"] = max(norm, key=norm.get)

            res["score"] = round(min(10.0,
                (norm.get("Angry", 0) * 9 + norm.get("Fear", 0) * 7 + norm.get("Sad", 0) * 4) * 10), 1)
            self._draw(bgr_frame, res)

        return res, bgr_frame

    def _estimate(self, lm):
        lc = lm[61];  rc = lm[291]
        t  = lm[13];  b  = lm[14]
        lb = lm[70];  rb = lm[300]
        li = lm[107]; ri = lm[336]
        le = lm[159]; re = lm[386]
        le2= lm[145]; re2= lm[374]
        el = lm[33];  er = lm[263]

        lip   = (t.y + b.y) / 2
        corY  = (lc.y + rc.y) / 2
        eyeD  = _d(el, er)
        smile = _c((lip - corY) * 80 + 0.5)
        frown = _c((corY - lip) * 80 + 0.5)
        bLift = _c(((le.y + re.y)/2 - (lb.y + rb.y)/2) * 35)
        furr  = _c(1.0 - (_d(li, ri) / (eyeD + 1e-6)) * 1.6)
        mh    = abs(t.y - b.y)
        mw    = _d(lm[61], lm[291])
        mar   = _c(mh / (mw + 1e-6))
        leh   = abs(le.y - le2.y) / (_d(el, lm[133]) + 1e-6)
        reh   = abs(re.y - re2.y) / (_d(lm[362], er) + 1e-6)
        wide  = _c(((leh + reh) / 2) * 8 - 1.5)

        raw = {
            "Happy":     smile * (1 - frown) * 0.9,
            "Sad":       frown * (1 - smile) * 0.7,
            "Angry":     frown * furr * 0.85,
            "Surprised": bLift * mar * wide * 0.9,
            "Fear":      bLift * (1 - smile) * mar * 0.75,
            "Neutral":   0.0,
        }
        s = sum(raw.values()) or 1e-6
        raw["Neutral"] = _c(1.0 - s * 0.85, 0.05, 1.0)
        t2 = sum(raw.values()) or 1.0
        return {k: v / t2 for k, v in raw.items()}

    def _draw(self, frame, res):
        h, w = frame.shape[:2]
        em = res["emotions"]
        dom = res["dominant"]
        ov = frame.copy()
        cv2.rectangle(ov, (0, h - 165), (205, h), (8, 12, 22), -1)
        cv2.addWeighted(ov, 0.65, frame, 0.35, 0, frame)
        y = h - 152
        for emo in EMOTIONS:
            pct = int(em.get(emo, 0) * 100)
            col = COLORS[emo]
            bw  = int(pct * 1.4)
            th  = 2 if emo == dom else 1
            cv2.putText(frame, f"{emo[:4]}:{pct:3d}%", (6, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, col, th)
            cv2.rectangle(frame, (74, y - 9), (74 + bw, y - 2), col, -1)
            y += 23
        cv2.putText(frame, f"Emotion: {dom}", (6, h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS[dom], 2)

    def release(self): self.face_mesh.close()


if __name__ == "__main__":
    det = EmotionDetector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): print("Cannot open camera"); exit(1)
    print("SafeDrive.ai — Emotion Detection  (Q to quit)")
    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)
        res, frame = det.process(frame)
        print(f"\rDominant: {res['dominant']:10s}  Score={res['score']}", end="")
        cv2.imshow("SafeDrive.ai - Emotion", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release(); cv2.destroyAllWindows(); det.release()
