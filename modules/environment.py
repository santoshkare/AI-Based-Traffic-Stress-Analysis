"""
Environment Detection Module
Software-based visibility analysis using OpenCV — no sensors required.
Detects: Fog (contrast), Low-light (brightness), Blur (Laplacian variance).
"""

import cv2
import numpy as np


# Thresholds (tune to your environment)
BRIGHTNESS_THRESHOLD  = 50    # mean pixel value < this → low light
FOG_THRESHOLD         = 40    # std dev of pixel values < this → foggy
BLUR_THRESHOLD        = 80    # Laplacian variance < this → blurry

VISIBILITY_LABELS = {
    0: "Clear",
    1: "Low-Light",
    2: "Fog",
    3: "Blurry"
}


class EnvironmentDetector:
    def __init__(self):
        pass

    def _brightness(self, gray):
        return float(np.mean(gray))

    def _contrast(self, gray):
        return float(np.std(gray))

    def _blur_score(self, gray):
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    def analyze_frame(self, frame):
        """
        Analyse a BGR frame for visibility conditions.
        Returns a result dict and annotated frame.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        brightness  = self._brightness(gray)
        contrast    = self._contrast(gray)
        blur        = self._blur_score(gray)

        low_light = brightness < BRIGHTNESS_THRESHOLD
        foggy     = contrast   < FOG_THRESHOLD
        blurry    = blur       < BLUR_THRESHOLD

        # Priority order: fog > low-light > blurry > clear
        if foggy:
            condition = 2   # Fog
        elif low_light:
            condition = 1   # Low-Light
        elif blurry:
            condition = 3   # Blurry
        else:
            condition = 0   # Clear

        label = VISIBILITY_LABELS[condition]

        # Visibility sub-score (0-10)
        score = 0
        if foggy:      score += 5
        if low_light:  score += 4
        if blurry:     score += 3
        score = min(10, score)

        result = {
            "condition": label,
            "condition_id": condition,
            "brightness": round(brightness, 1),
            "contrast":   round(contrast,   1),
            "blur_score": round(blur,        1),
            "low_light":  low_light,
            "foggy":      foggy,
            "blurry":     blurry,
            "score":      score
        }

        # Annotate frame
        color_map = {0: (0,255,0), 1:(0,165,255), 2:(200,200,200), 3:(255,0,255)}
        color = color_map.get(condition, (0,255,0))
        cv2.putText(frame, f"Visibility: {label}", (10, frame.shape[0]-40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Bright:{brightness:.0f} Blur:{blur:.0f}", (10, frame.shape[0]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        return result, frame
