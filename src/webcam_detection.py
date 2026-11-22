"""
src/webcam_detection.py
Phase 4 – Live Webcam Face Detection.

Captures live video from the laptop webcam, detects faces using the
Haar Cascade pipeline, draws bounding boxes with corner accents, and
overlays a real-time HUD (face count, FPS, shortcuts).

Keyboard shortcuts:
  q / ESC – quit
"""

import time
import cv2
import numpy as np
from typing import Optional, List, Tuple

from src.face_recognition import detect_faces


# ──────────────────────────────────────────────────────────────────────────────
# Camera helpers
# ──────────────────────────────────────────────────────────────────────────────

def initialize_camera(index: int = 0) -> Optional[cv2.VideoCapture]:
    """
    Opens the webcam at the given index.

    Tries the requested index first, then falls back to index 1.
    Returns a VideoCapture object on success, None on failure.
    """
    for cam_idx in ([index] if index != 0 else [0, 1]):
        cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
        if cap is not None and cap.isOpened():
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print(f"[Camera] Initialized on index {cam_idx}")
                return cap
            cap.release()

    print("[Camera] ERROR: Unable to open any webcam. Check permissions and connections.")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Drawing helpers
# ──────────────────────────────────────────────────────────────────────────────

def draw_bounding_box(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    corner_len: int = 18,
) -> np.ndarray:
    """
    Draws a full rectangle plus L-shaped corner accents on the frame.
    Returns the modified frame (in-place edit).
    """
    x, y, w, h = bbox

    # Full rectangle (thin, semi-transparent impression)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

    # Corner accents (thicker, more visible)
    t = thickness + 1
    # Top-left
    cv2.line(frame, (x, y), (x + corner_len, y), color, t)
    cv2.line(frame, (x, y), (x, y + corner_len), color, t)
    # Top-right
    cv2.line(frame, (x + w, y), (x + w - corner_len, y), color, t)
    cv2.line(frame, (x + w, y), (x + w, y + corner_len), color, t)
    # Bottom-left
    cv2.line(frame, (x, y + h), (x + corner_len, y + h), color, t)
    cv2.line(frame, (x, y + h), (x, y + h - corner_len), color, t)
    # Bottom-right
    cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), color, t)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), color, t)

    return frame


def draw_hud(
    frame: np.ndarray,
    face_count: int,
    fps: float,
) -> np.ndarray:
    """
    Draws the top HUD bar: system title, face count, FPS and shortcut hint.
    """
    h, w = frame.shape[:2]

    # Dark semi-transparent banner
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 44), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(frame, "SMART SOCIETY SECURITY", (8, 28),
                font, 0.65, (0, 220, 255), 2, cv2.LINE_AA)

    face_txt = f"Faces: {face_count}"
    cv2.putText(frame, face_txt, (w // 2 - 50, 28),
                font, 0.60, (255, 255, 255), 1, cv2.LINE_AA)

    fps_txt = f"FPS: {fps:.1f}"
    cv2.putText(frame, fps_txt, (w - 110, 28),
                font, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

    # Bottom shortcut hint
    cv2.putText(frame, "Press  Q / ESC  to exit", (8, h - 10),
                font, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

    # No-face message
    if face_count == 0:
        msg = "No face detected"
        (tw, th), _ = cv2.getTextSize(msg, font, 0.75, 2)
        cx = (w - tw) // 2
        cy = (h + th) // 2
        cv2.putText(frame, msg, (cx, cy), font, 0.75, (100, 100, 255), 2, cv2.LINE_AA)

    return frame


# ──────────────────────────────────────────────────────────────────────────────
# Main detection loop
# ──────────────────────────────────────────────────────────────────────────────

def run_live_detection(
    camera_index: int = 0,
    max_frames: int = 0,
    mock_image_path: Optional[str] = None,
) -> None:
    """
    Runs the live face-detection loop.

    Parameters
    ----------
    camera_index    : Webcam device index (default 0).
    max_frames      : Stop after this many frames (0 = run until key pressed).
                      Used for automated testing.
    mock_image_path : If provided, uses this static image instead of a live
                      camera feed.  Used for testing without a webcam.
    """
    # ── Mock-image mode (for headless / automated testing) ──────────────────
    if mock_image_path:
        import os
        if not os.path.exists(mock_image_path):
            print(f"[Detection] Mock image not found: {mock_image_path}")
            return

        frame = cv2.imread(mock_image_path)
        if frame is None:
            print("[Detection] Could not read mock image.")
            return

        faces = detect_faces(frame)
        for bbox in faces:
            draw_bounding_box(frame, bbox)
        draw_hud(frame, len(faces), fps=0.0)
        print(f"[Detection] Mock mode – {len(faces)} face(s) detected.")

        if max_frames > 0:          # headless: don't open a window
            return

        cv2.imshow("Smart Society Security – Detection", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # ── Live webcam mode ─────────────────────────────────────────────────────
    cap = initialize_camera(camera_index)
    if cap is None:
        return

    frame_count = 0
    fps = 0.0
    t0 = time.time()

    print("[Detection] Live feed running.  Press Q or ESC to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[Detection] WARNING: Failed to read frame. Retrying…")
                time.sleep(0.05)
                continue

            # ── Face detection ───────────────────────────────────────────────
            faces = detect_faces(frame)

            for bbox in faces:
                draw_bounding_box(frame, bbox)

            # ── FPS computation ──────────────────────────────────────────────
            frame_count += 1
            elapsed = time.time() - t0
            if elapsed >= 0.5:
                fps = frame_count / elapsed
                frame_count = 0
                t0 = time.time()

            draw_hud(frame, len(faces), fps)

            cv2.imshow("Smart Society Security – Detection (Phase 4)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):   # q or ESC
                print("[Detection] Exit key pressed.")
                break

            if max_frames > 0 and frame_count >= max_frames:
                break

    except KeyboardInterrupt:
        print("[Detection] Interrupted.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[Detection] Camera released.")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_live_detection()
