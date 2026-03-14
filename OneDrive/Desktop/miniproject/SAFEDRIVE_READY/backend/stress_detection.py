"""
SafeDrive.ai - Module 3: Voice-Based Stress Detection
======================================================
Objective 3: Analyze stress using voice signals

Features: MFCC (13) + Pitch + RMS Energy + ZCR  →  32 total
Model:    RandomForestClassifier (scikit-learn)
Classes:  Normal | Mild Stress | High Stress

Run: python stress_detection.py
"""

import numpy as np
import librosa
from sklearn.ensemble        import RandomForestClassifier
from sklearn.preprocessing   import StandardScaler
from sklearn.model_selection import train_test_split

SR       = 22050
DURATION = 2
N_MFCC   = 13
LABELS   = {0: "Normal", 1: "Mild Stress", 2: "High Stress"}
SCORES   = {0: 0, 1: 4, 2: 8}


def extract_features(audio, sr=SR):
    feats = []
    mfcc  = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
    feats.extend(np.mean(mfcc, axis=1))
    feats.extend(np.std(mfcc,  axis=1))
    try:
        f0, vf, _ = librosa.pyin(audio, fmin=50, fmax=500, sr=sr)
        v = f0[vf] if vf is not None else np.array([0.0])
        feats += [float(np.nanmean(v)) if len(v) else 0.0,
                  float(np.nanstd(v))  if len(v) else 0.0]
    except Exception:
        feats += [0.0, 0.0]
    rms = librosa.feature.rms(y=audio)
    feats += [float(np.mean(rms)), float(np.std(rms))]
    zcr = librosa.feature.zero_crossing_rate(audio)
    feats += [float(np.mean(zcr)), float(np.std(zcr))]
    return np.array(feats, dtype=np.float32)


class StressDetector:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model  = RandomForestClassifier(n_estimators=100, max_depth=12,
                                             random_state=42, n_jobs=-1)
        self._build_demo_model()

    def _build_demo_model(self):
        np.random.seed(42)
        n  = 500
        nf = N_MFCC * 2 + 6   # 32
        X = np.vstack([
            np.random.randn(n, nf) * 0.40,           # Normal
            np.random.randn(n, nf) * 0.70 + 0.50,    # Mild
            np.random.randn(n, nf) * 1.10 + 1.20,    # High
        ])
        y = np.array([0]*n + [1]*n + [2]*n)
        Xt, Xv, yt, yv = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        self.scaler.fit(Xt)
        self.model.fit(self.scaler.transform(Xt), yt)
        acc = self.model.score(self.scaler.transform(Xv), yv)
        print(f"[StressDetector] Ready  accuracy={acc:.0%}  (demo model)")

    def predict(self, audio, sr=SR):
        feats  = extract_features(audio, sr).reshape(1, -1)
        pred   = int(self.model.predict(self.scaler.transform(feats))[0])
        probs  = self.model.predict_proba(self.scaler.transform(feats))[0]
        return {"level": LABELS[pred], "label": pred,
                "score": SCORES[pred], "confidence": round(float(np.max(probs)), 2)}

    def predict_from_mic(self, duration=DURATION, sr=SR):
        try:
            import sounddevice as sd
            audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
            sd.wait()
            return self.predict(audio.flatten(), sr)
        except ImportError:
            return {"level": "Normal", "label": 0, "score": 0, "confidence": 0.0}

    def predict_from_file(self, path):
        audio, sr = librosa.load(path, sr=SR, mono=True)
        return self.predict(audio, sr)


if __name__ == "__main__":
    det   = StressDetector()
    dummy = np.zeros(SR * 2, dtype=np.float32)
    res   = det.predict(dummy)
    print(f"\nDemo prediction: {res['level']}  score={res['score']}  conf={res['confidence']:.0%}")
    print("\nTo use mic: pip install sounddevice  then  det.predict_from_mic()")
