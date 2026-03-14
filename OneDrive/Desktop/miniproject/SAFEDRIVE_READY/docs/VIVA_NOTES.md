# SafeDrive.ai — Viva Notes

## Demo Steps
1. Open `frontend/index.html` in Chrome
2. Login: `demo@test.com` / `demo1234`
3. Click ▶ Start → allow camera + mic
4. **Drowsy**: half-close eyes 2s → EAR drops → DROWSY alert
5. **Yawn**: open mouth wide → MAR rises → YAWN alert
6. **Emotion**: smile → Happy rises; frown → Angry/Sad rises
7. **Visibility**: cover lens → blur/low-light alert fires
8. **Child**: click Engine OFF → wave hand → CHILD ALERT
9. Show Risk Score gauge climbing from green → yellow → red

---

## Key Formulas

**EAR:**  `(||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)`  → threshold 0.25, 18 frames
**MAR:**  `(A+B+C) / (2D)`  → threshold 0.60, 12 frames
**Risk:** `D×0.35 + S×0.25 + E×0.20 + C×0.20`  smoothed 30 frames

---

## Viva Q&A

**Q: What is MediaPipe?**
A: Google's real-time ML framework. FaceMesh detects 468 3D facial landmarks.

**Q: Why EAR threshold 0.25?**
A: From Soukupová & Čech (2016). Normal eye EAR ≈ 0.30–0.35; below 0.25 indicates closure.

**Q: Why 18 frames?**
A: At 20fps = 0.9s. Normal blink = 0.1–0.4s. Sustained closure > 0.9s = drowsy.

**Q: What is MFCC?**
A: Mel Frequency Cepstral Coefficients — represent vocal tract shape from audio spectrum on Mel scale.

**Q: What is ZCR?**
A: Zero Crossing Rate — how often audio signal changes sign. Stressed speech has higher ZCR.

**Q: Why RandomForest?**
A: Handles noisy features, no overfitting, fast inference, gives probability outputs.

**Q: How does visibility work without sensors?**
A: Fog → low contrast, Low-light → low brightness, Blur → low Laplacian variance. Pure pixel math.

**Q: How does child detection work?**
A: Frame differencing. Mean pixel difference > 8 AND engine OFF → motion alert.

**Q: What is rolling average for?**
A: Smooths out single-frame spikes (blinks). 30-frame average fires only for sustained conditions.

**Q: Limitations?**
A: Needs good lighting, synthetic stress training data, single face only, no GPS.

---

## Key Terms

| Term | Meaning |
|------|---------|
| EAR | Eye Aspect Ratio |
| MAR | Mouth Aspect Ratio |
| MFCC | Mel Frequency Cepstral Coefficients |
| ZCR | Zero Crossing Rate |
| pYIN | Probabilistic YIN pitch detection |
| MediaPipe | Google ML pipeline framework |
| Laplacian | Edge-detection operator (blur detection) |
| Rolling Average | Sliding window mean (noise smoothing) |
| RandomForest | Ensemble of decision trees |
| WebAssembly | Browser near-native binary execution |
