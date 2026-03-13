"""
SafeDrive.ai — Demo Script (No Camera Required)
Simulates all detection modules and prints risk score to terminal.
Run: python demo.py
"""

import numpy as np
import time
import sys

def simulate_ear(t):
    """Simulate EAR that drops (drowsy) every ~15 seconds."""
    base = 0.32 + 0.05 * np.sin(t * 0.3)
    if int(t) % 20 < 5:
        return max(0.15, base - 0.15)
    return base

def simulate_mar(t):
    """Simulate MAR that rises (yawn) periodically."""
    if int(t) % 30 in range(3, 8):
        return 0.72
    return 0.30 + 0.05 * np.random.randn()

def simulate_stress(t):
    if int(t) % 25 in range(5, 10):
        return {"level": "High Stress", "score": 8}
    if int(t) % 15 in range(3, 6):
        return {"level": "Mild Stress", "score": 4}
    return {"level": "Normal", "score": 0}

def simulate_visibility(t):
    if int(t) % 40 in range(10, 16):
        return {"condition": "Fog", "score": 5}
    if int(t) % 35 in range(5, 9):
        return {"condition": "Low-Light", "score": 4}
    return {"condition": "Clear", "score": 0}


def main():
    print("=" * 55)
    print("  SafeDrive.ai — Demo Mode (Simulated Sensors)")
    print("  Press Ctrl+C to quit")
    print("=" * 55)

    from modules.risk_engine import RiskEngine
    engine = RiskEngine()

    t = 0
    try:
        while True:
            ear  = simulate_ear(t)
            mar  = simulate_mar(t)
            drowsy  = ear < 0.25
            yawning = mar > 0.65

            stress_info = simulate_stress(t)
            vis_info    = simulate_visibility(t)

            drowsy_score = 7 if drowsy else (4 if yawning else 0)
            risk = engine.update(
                drowsiness_score  = drowsy_score,
                stress_score      = stress_info["score"],
                environment_score = vis_info["score"],
                child_score       = 0
            )

            # Terminal output
            bar_len = int(risk["smooth_score"] * 5)
            bar = "█" * bar_len + "░" * (50 - bar_len)
            color = "\033[92m"  # green
            if risk["smooth_score"] >= 3: color = "\033[93m"
            if risk["smooth_score"] >= 6: color = "\033[91m"
            reset = "\033[0m"

            sys.stdout.write("\033[2J\033[H")  # clear screen
            print("=" * 55)
            print("  SafeDrive.ai — LIVE DEMO")
            print("=" * 55)
            print(f"\n  Risk Score : {color}{risk['smooth_score']:.1f} / 10.0{reset}")
            print(f"  Risk Level : {color}{risk['level']}{reset}")
            print(f"  [{bar}]")
            print()
            print(f"  👁  EAR       : {ear:.3f}  {'⚠ DROWSY' if drowsy else 'OK'}")
            print(f"  😮 MAR       : {mar:.3f}  {'⚠ YAWNING' if yawning else 'OK'}")
            print(f"  🎤 Stress    : {stress_info['level']} (score {stress_info['score']})")
            print(f"  🌫 Visibility: {vis_info['condition']} (score {vis_info['score']})")
            print()
            print("  Recent alerts:")
            for a in engine.get_alerts(3):
                print(f"    [{a['time']}] {a['message']} — score {a['score']}")
            print()
            print("  (Run app.py to open the full web dashboard)")
            print("=" * 55)

            time.sleep(1)
            t += 1
    except KeyboardInterrupt:
        print("\n\nDemo stopped.")


if __name__ == "__main__":
    main()
