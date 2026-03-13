"""
Stress Detection Module
Voice-based stress analysis using MFCC, Pitch, Energy, and ZCR features.
Uses librosa for feature extraction and scikit-learn for classification.
"""

import numpy as np
import librosa
import io
import wave
import struct
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


STRESS_LEVELS = ["Normal", "Mild Stress", "High Stress"]
SAMPLE_RATE   = 22050
DURATION      = 3      # seconds per analysis window
N_MFCC        = 13


def extract_features(audio_data, sr=SAMPLE_RATE):
    """Extract MFCC, pitch, energy, and ZCR from audio array."""
    features = []

    # MFCCs
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=N_MFCC)
    features.extend(np.mean(mfccs, axis=1).tolist())
    features.extend(np.std(mfccs, axis=1).tolist())

    # Pitch (F0) via YIN
    try:
        f0, voiced_flag, _ = librosa.pyin(audio_data, fmin=50, fmax=500, sr=sr)
        f0_voiced = f0[voiced_flag] if voiced_flag is not None else np.array([0.0])
        features.append(float(np.nanmean(f0_voiced)) if len(f0_voiced) > 0 else 0.0)
        features.append(float(np.nanstd(f0_voiced))  if len(f0_voiced) > 0 else 0.0)
    except Exception:
        features.extend([0.0, 0.0])

    # Energy (RMS)
    rms = librosa.feature.rms(y=audio_data)
    features.append(float(np.mean(rms)))
    features.append(float(np.std(rms)))

    # Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(audio_data)
    features.append(float(np.mean(zcr)))
    features.append(float(np.std(zcr)))

    return np.array(features)


class StressDetector:
    def __init__(self, model_path=None):
        self.model   = None
        self.scaler  = StandardScaler()
        self._build_demo_model()   # pretrained demo weights

    def _build_demo_model(self):
        """
        Build a lightweight demo model with synthetic training data.
        In production, replace with a real labelled dataset.
        """
        np.random.seed(42)
        n = 300
        n_features = N_MFCC * 2 + 6   # 32

        # Simulate three stress classes
        X0 = np.random.randn(n, n_features) * 0.5                 # normal
        X1 = np.random.randn(n, n_features) * 0.8  + 0.5          # mild
        X2 = np.random.randn(n, n_features) * 1.2  + 1.2          # high
        X  = np.vstack([X0, X1, X2])
        y  = np.array([0]*n + [1]*n + [2]*n)

        self.scaler.fit(X)
        Xs = self.scaler.transform(X)
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.model.fit(Xs, y)

    def analyze(self, audio_bytes, sr=SAMPLE_RATE):
        """
        Analyze raw PCM bytes (float32 mono) and return stress result dict.
        audio_bytes: bytes object of float32 audio samples.
        """
        try:
            audio = np.frombuffer(audio_bytes, dtype=np.float32)
            if len(audio) < sr * 0.5:
                return {"level": "Normal", "label": 0, "score": 0, "confidence": 0.0}

            feats = extract_features(audio, sr).reshape(1, -1)
            feats_scaled = self.scaler.transform(feats)
            pred   = int(self.model.predict(feats_scaled)[0])
            probs  = self.model.predict_proba(feats_scaled)[0]
            conf   = float(np.max(probs))

            score_map = {0: 0, 1: 4, 2: 8}
            return {
                "level":      STRESS_LEVELS[pred],
                "label":      pred,
                "score":      score_map[pred],
                "confidence": round(conf, 2)
            }
        except Exception as e:
            return {"level": "Normal", "label": 0, "score": 0, "confidence": 0.0,
                    "error": str(e)}

    def analyze_file(self, filepath):
        """Analyze a .wav file."""
        audio, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)
        audio_bytes = audio.astype(np.float32).tobytes()
        return self.analyze(audio_bytes, sr)
