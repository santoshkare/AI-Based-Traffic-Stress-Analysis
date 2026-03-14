"""
SafeDrive.ai - Master Python Runner (All Modules)
==================================================
Runs all 5 detection modules simultaneously in one OpenCV window.

Run:      python run_all.py
Controls: E = engine ON/OFF  |  R = reset score  |  Q = quit
"""

import cv2, threading, time, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from drowsiness_detection  import DrowsinessDetector
from emotion_detection     import EmotionDetector
from stress_detection      import StressDetector
from visibility_detection  import VisibilityDetector, ChildPresenceDetector
from risk_engine           import RiskEngine

# ── Instantiate all modules ───────────────────────────────────
drow_det  = DrowsinessDetector()
emo_det   = EmotionDetector()
str_det   = StressDetector()
vis_det   = VisibilityDetector()
child_det = ChildPresenceDetector()
risk_eng  = RiskEngine(window=30)

# ── Stress runs in background thread (mic) ────────────────────
_slock  = threading.Lock()
_sres   = {"level":"Normal","score":0,"confidence":0.0}
_srun   = True

def _stress_loop():
    while _srun:
        try:
            r = str_det.predict_from_mic(duration=2)
            with _slock: _sres.update(r)
        except Exception: time.sleep(2)

threading.Thread(target=_stress_loop, daemon=True).start()

# ── HUD overlay ───────────────────────────────────────────────
def draw_hud(frame, risk, stress, vis, child, drow, emo):
    h, w = frame.shape[:2]
    ov = frame.copy()
    cv2.rectangle(ov, (w-275,0), (w,h), (5,8,18), -1)
    cv2.addWeighted(ov, 0.75, frame, 0.25, 0, frame)
    sc  = risk["score"]
    col = (0,220,80) if sc<3 else (0,165,255) if sc<6 else (0,0,230)

    def put(txt, y, c=(160,190,220), s=0.52, t=1):
        cv2.putText(frame, txt, (w-270, y), cv2.FONT_HERSHEY_SIMPLEX, s, c, t)

    put(f"RISK: {sc:.1f}/10", 22, col, 0.65, 2)
    put(f"Level: {risk['level']}", 44, col)
    bw = int((sc/10)*240)
    cv2.rectangle(frame, (w-270,52), (w-270+bw,60), col, -1)
    cv2.rectangle(frame, (w-270,52), (w-30,60), (30,50,70), 1)

    put("─"*36, 74, (20,38,60))
    def srow(lbl, val, y, bc):
        put(f"{lbl}: {val:.1f}", y, (120,155,185))
        cv2.rectangle(frame,(w-145,y-10),(w-145+int(val/10*135),y-3),bc,-1)

    srow("Drowsiness ", risk["sub"]["drowsiness"],  96,  (0,60,220))
    srow("Stress     ", risk["sub"]["stress"],      116, (120,0,220))
    srow("Environment", risk["sub"]["environment"], 136, (180,90,0))
    srow("Child      ", risk["sub"]["child"],       156, (0,0,220))
    put("─"*36, 164, (20,38,60))

    def st(lbl, ov, bv, bad, y):
        c = (0,0,220) if bad else (0,200,80)
        put(f"{lbl}: {bv if bad else ov}", y, c)

    st("EAR    ", f"{drow.get('ear',0):.3f}",  "DROWSY  ", drow.get("drowsy"),  182)
    st("MAR    ", f"{drow.get('mar',0):.3f}",  "YAWNING ", drow.get("yawning"), 200)
    st("Emotion", emo.get("dominant","?"),      emo.get("dominant","?"),  False,  218)
    st("Stress ", stress["level"],              stress["level"],
       stress["level"]=="High Stress", 236)
    st("Visib  ", vis["condition"], vis["condition"], vis["condition"]!="Clear", 254)
    st("Child  ", "OK", "ALERT!", child.get("alert"), 272)
    put("─"*36, 280, (20,38,60))
    put(f"Engine: {'ON' if child_det.engine_on else 'OFF'}", 298)
    put(f"Blinks: {drow.get('blinks',0)}", 316)


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened(): print("ERROR: Cannot open camera"); sys.exit(1)

    print("\n" + "="*55)
    print("  SafeDrive.ai — Full Python Runner")
    print("  All 5 modules + Risk Engine active")
    print("  E=engine toggle  R=reset  Q=quit")
    print("="*55 + "\n")

    fc=0; fl=time.time(); fps=0
    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)

        d_r, frame = drow_det.process(frame)
        e_r, frame = emo_det.process(frame)
        v_r, frame = vis_det.analyze(frame)
        c_r, frame = child_det.detect(frame)
        with _slock: s_r = dict(_sres)

        risk = risk_eng.update(
            drowsiness=d_r.get("score",0), stress=s_r.get("score",0),
            environment=v_r.get("score",0), child=c_r.get("score",0))

        draw_hud(frame, risk, s_r, v_r, c_r, d_r, e_r)

        fc += 1
        if time.time()-fl >= 1.0:
            fps=fc; fc=0; fl=time.time()
        cv2.putText(frame,f"FPS:{fps}",(8,frame.shape[0]-8),cv2.FONT_HERSHEY_SIMPLEX,0.5,(40,70,100),1)

        sys.stdout.write(f"\r  Risk={risk['score']:.1f} ({risk['level']:12s})  "
                         f"EAR={d_r.get('ear',0):.3f}  Stress={s_r['level']:12s}  "
                         f"Vis={v_r['condition']:10s}  FPS={fps}")
        sys.stdout.flush()

        cv2.imshow("SafeDrive.ai — Real-Time Safety Monitor", frame)
        key = cv2.waitKey(1) & 0xFF
        if   key == ord('q'): break
        elif key == ord('e'):
            child_det.set_engine(not child_det.engine_on)
            print(f"\nEngine: {'ON' if child_det.engine_on else 'OFF'}")
        elif key == ord('r'):
            risk_eng.reset(); print("\nRisk score reset.")

    global _srun; _srun = False
    cap.release(); cv2.destroyAllWindows()
    drow_det.release(); emo_det.release()
    print("\n\nSession ended.")


if __name__ == "__main__":
    main()
