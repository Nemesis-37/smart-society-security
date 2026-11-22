"""
src/security_gate.py
Phase 6 – Final Security Gate Interface.

Integrates webcam, face detection and recognition into a single OpenCV
display loop with professional HUD overlays:

  GREEN box + "ENTRY ALLOWED" + name  → registered resident
  RED   box + "ENTRY REJECTED" + "Unknown Person" → unregistered
  "GATE IDLE – AWAITING ENTRANT"      → no face detected

Keyboard shortcuts (live mode):
  q / ESC   – quit
  +  / =    – raise recognition threshold by 0.05
  -  / _    – lower recognition threshold by 0.05
  r         – reload resident database (hot reload)
"""

import time
import cv2
import numpy as np
from typing import Optional, Tuple

from src.recognition_engine import (
    SecurityRecognizer,
    GATE_ALLOWED,
    GATE_REJECTED,
    GATE_NO_FACE,
)
from src.webcam_detection import initialize_camera


# ──────────────────────────────────────────────────────────────────────────────
# Color palette
# ──────────────────────────────────────────────────────────────────────────────

GREEN  = (0,   220,  60)
RED    = (0,    30, 220)
YELLOW = (0,   210, 240)
CYAN   = (220, 210,   0)
WHITE  = (255, 255, 255)
GRAY   = (160, 160, 160)
DARK   = ( 20,  20,  20)


# ──────────────────────────────────────────────────────────────────────────────
# Drawing helpers
# ──────────────────────────────────────────────────────────────────────────────

def _corner_box(
    frame: np.ndarray,
    x: int, y: int, w: int, h: int,
    color: Tuple,
    thickness: int = 2,
    clen: int = 20,
) -> None:
    """Draws a full rectangle plus L-shaped corner accents."""
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    t = thickness + 1
    cv2.line(frame, (x, y),         (x + clen, y),         color, t)
    cv2.line(frame, (x, y),         (x, y + clen),         color, t)
    cv2.line(frame, (x + w, y),     (x + w - clen, y),     color, t)
    cv2.line(frame, (x + w, y),     (x + w, y + clen),     color, t)
    cv2.line(frame, (x, y + h),     (x + clen, y + h),     color, t)
    cv2.line(frame, (x, y + h),     (x, y + h - clen),     color, t)
    cv2.line(frame, (x + w, y + h), (x + w - clen, y + h), color, t)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - clen), color, t)


def _label_banner(
    frame: np.ndarray,
    x: int, y: int, w: int,
    label: str, sublabel: str,
    color: Tuple,
) -> None:
    """Draws a small coloured banner above the bounding box."""
    font   = cv2.FONT_HERSHEY_SIMPLEX
    banner_h = 46
    bx, by = x, max(0, y - banner_h)
    # Dark semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (bx, by), (bx + w, y), DARK, -1)
    cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

    cv2.putText(frame, label,    (bx + 6, by + 18), font, 0.55, color, 2, cv2.LINE_AA)
    cv2.putText(frame, sublabel, (bx + 6, by + 38), font, 0.47, WHITE, 1, cv2.LINE_AA)


def _draw_top_hud(
    frame: np.ndarray,
    gate_status: str,
    resident_count: int,
    threshold: float,
    fps: float,
) -> None:
    """Draws the top HUD bar with system info."""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), DARK, -1)
    cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(frame, "SMART SOCIETY SECURITY SYSTEM", (8, 32),
                font, 0.65, CYAN, 2, cv2.LINE_AA)

    # Gate status chip (right side)
    chip_color = GREEN if gate_status == GATE_ALLOWED else (RED if gate_status == GATE_REJECTED else GRAY)
    cv2.putText(frame, gate_status, (w - 260, 32),
                font, 0.60, chip_color, 2, cv2.LINE_AA)

    # Bottom row
    info = f"Residents: {resident_count}   Threshold: {threshold:.2f}   FPS: {fps:.1f}   [+/-] thresh  [R] reload  [Q] quit"
    cv2.putText(frame, info, (8, h - 10),
                font, 0.38, GRAY, 1, cv2.LINE_AA)


def _draw_idle_message(frame: np.ndarray) -> None:
    h, w = frame.shape[:2]
    msg  = "GATE IDLE \u2013 AWAITING ENTRANT"
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(msg, font, 0.80, 2)
    cv2.putText(frame, msg, ((w - tw) // 2, (h + th) // 2),
                font, 0.80, YELLOW, 2, cv2.LINE_AA)


# ──────────────────────────────────────────────────────────────────────────────
# Annotate a frame with recognition results
# ──────────────────────────────────────────────────────────────────────────────

def annotate_frame(frame: np.ndarray, results: list, gate_status: str) -> np.ndarray:
    """
    Draws bounding boxes, banners and HUD for all recognition results.
    Can be called in both live and mock-image modes.
    """
    for (bbox, result) in results:
        x, y, w, h = bbox
        allowed     = result["is_recognized"]
        box_color   = GREEN if allowed else RED
        decision    = result["decision"]
        name        = result["name"]
        dist_txt    = f"Dist: {result['distance']:.3f}"

        _corner_box(frame, x, y, w, h, box_color)
        sub = name if allowed else "Unknown Person"
        _label_banner(frame, x, y, w, decision, sub, box_color)

        # Distance label below box
        cv2.putText(frame, dist_txt,
                    (x, y + h + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, GRAY, 1, cv2.LINE_AA)

    if gate_status == GATE_NO_FACE:
        _draw_idle_message(frame)

    return frame


# ──────────────────────────────────────────────────────────────────────────────
# Main security gate loop
# ──────────────────────────────────────────────────────────────────────────────

def run_security_system(
    camera_index:    int   = 0,
    threshold:       float = 0.50,
    max_frames:      int   = 0,
    mock_image_path: Optional[str] = None,
    db_path:         Optional[str] = None,
) -> None:
    """
    Launches the Smart Society Security Gate.

    Parameters
    ----------
    camera_index    : Webcam device index (default 0).
    threshold       : Face match threshold (default 0.50).
    max_frames      : Auto-stop after N frames (0 = run until key press).
    mock_image_path : Use a static image instead of live webcam (testing).
    db_path         : Custom SQLite database path.
    """
    recognizer = SecurityRecognizer(db_path=db_path, threshold=threshold)
    print(f"[Gate] {recognizer.resident_count} resident(s) loaded. Threshold: {threshold:.2f}")

    # ── Mock-image mode ───────────────────────────────────────────────────────
    if mock_image_path:
        import os
        if not os.path.exists(mock_image_path):
            print(f"[Gate] Mock image not found: {mock_image_path}")
            return

        frame = cv2.imread(mock_image_path)
        if frame is None:
            print("[Gate] Could not read mock image.")
            return

        results, gate_status = recognizer.process_frame(frame)
        annotate_frame(frame, results, gate_status)
        _draw_top_hud(frame, gate_status, recognizer.resident_count, recognizer.threshold, 0.0)

        for _, r in results:
            tag = "ALLOWED" if r["is_recognized"] else "REJECTED"
            print(f"  [{tag}] {r['name']}  dist={r['distance']:.4f}")

        if gate_status == GATE_NO_FACE:
            print("  [GATE] No face detected.")

        print(f"[Gate] Mock test complete – gate_status={gate_status}")

        if max_frames > 0:          # fully headless
            return

        cv2.imshow("Smart Society Security Gate", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # ── Live webcam mode ──────────────────────────────────────────────────────
    cap = initialize_camera(camera_index)
    if cap is None:
        return

    fps        = 0.0
    frame_cnt  = 0
    t0         = time.time()
    win_name   = "Smart Society Security Gate  –  Phase 6"

    print("[Gate] Running live security gate. Press Q/ESC to exit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            results, gate_status = recognizer.process_frame(frame)
            annotate_frame(frame, results, gate_status)

            # FPS
            frame_cnt += 1
            elapsed = time.time() - t0
            if elapsed >= 0.5:
                fps = frame_cnt / elapsed
                frame_cnt = 0
                t0 = time.time()

            _draw_top_hud(frame, gate_status, recognizer.resident_count, recognizer.threshold, fps)
            cv2.imshow(win_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                print("[Gate] Exit key pressed.")
                break
            elif key in (ord("+"), ord("=")):
                recognizer.threshold = min(1.0, round(recognizer.threshold + 0.05, 2))
                print(f"[Gate] Threshold → {recognizer.threshold:.2f}")
            elif key in (ord("-"), ord("_")):
                recognizer.threshold = max(0.10, round(recognizer.threshold - 0.05, 2))
                print(f"[Gate] Threshold → {recognizer.threshold:.2f}")
            elif key in (ord("r"), ord("R")):
                recognizer.reload_residents()

            if max_frames > 0 and frame_cnt >= max_frames:
                break

    except KeyboardInterrupt:
        print("[Gate] Interrupted.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[Gate] Shut down.")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_security_system()
