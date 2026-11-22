"""
Phase 6: Smart Society Security System - Integrated Live OpenCV Application.
Integrates live laptop webcam, Haar Cascade face detection, 128-D face encoding,
SQLite resident database lookup, and security access decisions:
  - Green ENTRY ALLOWED for registered residents (with resident name & ID)
  - Red ENTRY REJECTED for unknown individuals
  - Multi-face support & graceful no-face handling
  - Real-time threshold adjustment (+ / -) & database reload (r)
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np

from database.db_manager import DEFAULT_DB_PATH
from models.recognizer import SecurityRecognizer, DEFAULT_THRESHOLD


def draw_security_hud(
    frame: np.ndarray,
    gate_status: str,
    resident_count: int,
    threshold: float,
    fps: float,
    face_count: int,
):
    """
    Renders top security dashboard HUD banner with real-time gate status.
    """
    h, w, _ = frame.shape

    # Translucent dark header
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 68), (18, 18, 18), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    # Title
    cv2.putText(
        frame,
        "SMART SOCIETY SECURITY SYSTEM",
        (16, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Gate status indicator badge
    if gate_status == "ENTRY ALLOWED":
        status_text = "[ ACCESS GRANTED - WELCOME ]"
        status_color = (0, 220, 0)  # Green
    elif gate_status == "ENTRY REJECTED":
        status_text = "[ ACCESS DENIED - UNREGISTERED PERSON ]"
        status_color = (0, 0, 255)  # Red
    else:
        status_text = "[ GATE IDLE - AWAITING ENTRANT ]"
        status_color = (180, 180, 180)  # Gray

    cv2.putText(
        frame,
        status_text,
        (370, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        status_color,
        2,
        cv2.LINE_AA,
    )

    # Secondary Info Bar
    metrics_str = (
        f"Faces: {face_count} | Registered: {resident_count} | "
        f"Threshold: {threshold:.2f} [+/-] | FPS: {fps:.1f} | [r] Reload | [q] Exit"
    )
    cv2.putText(
        frame,
        metrics_str,
        (16, 54),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (200, 200, 200),
        1,
        cv2.LINE_AA,
    )


def draw_face_decision(
    frame: np.ndarray,
    bbox: tuple,
    match_result: dict,
):
    """
    Renders styled bounding box and security decision labels:
      - Green with "ENTRY ALLOWED" and Name for registered residents
      - Red with "ENTRY REJECTED" and "Unknown" for unregistered persons
    """
    x, y, w, h = bbox
    decision = match_result["decision"]
    is_allowed = (decision == "ENTRY ALLOWED")

    # Color scheme
    if is_allowed:
        box_color = (0, 220, 0)       # Green
        text_color = (255, 255, 255)   # White
        badge_bg = (0, 160, 0)        # Darker Green
    else:
        box_color = (0, 0, 255)       # Red
        text_color = (255, 255, 255)   # White
        badge_bg = (0, 0, 180)        # Darker Red

    # 1. Main Bounding Box
    thickness = 2
    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, thickness)

    # 2. Corner Brackets (for sleek security styling)
    corner_len = int(min(w, h) * 0.18)
    # Top-Left
    cv2.line(frame, (x, y), (x + corner_len, y), box_color, thickness + 2)
    cv2.line(frame, (x, y), (x, y + corner_len), box_color, thickness + 2)
    # Top-Right
    cv2.line(frame, (x + w, y), (x + w - corner_len, y), box_color, thickness + 2)
    cv2.line(frame, (x + w, y), (x + w, y + corner_len), box_color, thickness + 2)
    # Bottom-Left
    cv2.line(frame, (x, y + h), (x + corner_len, y + h), box_color, thickness + 2)
    cv2.line(frame, (x, y + h), (x, y + h - corner_len), box_color, thickness + 2)
    # Bottom-Right
    cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), box_color, thickness + 2)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), box_color, thickness + 2)

    # 3. Top Decision Banner: "ENTRY ALLOWED" or "ENTRY REJECTED"
    banner_text = f" {decision} "
    (tw, th), _ = cv2.getTextSize(banner_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    banner_y1 = max(0, y - th - 12)
    banner_y2 = y
    banner_x1 = x
    banner_x2 = x + tw + 10

    cv2.rectangle(frame, (banner_x1, banner_y1), (banner_x2, banner_y2), badge_bg, -1)
    cv2.putText(
        frame,
        banner_text,
        (banner_x1 + 4, banner_y2 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        text_color,
        2,
        cv2.LINE_AA,
    )

    # 4. Bottom Identity Tag: Resident Name & ID or "Unknown Person"
    if is_allowed:
        name_text = f"{match_result['name']} ({match_result['resident_id']})"
        sub_text = f"Dist: {match_result['distance']:.3f} | Conf: {match_result['confidence']}%"
    else:
        name_text = "Unknown Person"
        sub_text = f"Dist: {match_result['distance']:.3f} > {match_result['threshold']:.2f}"

    (nw, nh), _ = cv2.getTextSize(name_text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
    (sw, sh), _ = cv2.getTextSize(sub_text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)

    tag_w = max(nw, sw) + 14
    tag_h = nh + sh + 16
    tag_y1 = y + h
    tag_y2 = min(frame.shape[0], tag_y1 + tag_h)
    tag_x1 = x
    tag_x2 = min(frame.shape[1], x + tag_w)

    # Semi-transparent tag background
    tag_overlay = frame.copy()
    cv2.rectangle(tag_overlay, (tag_x1, tag_y1), (tag_x2, tag_y2), (25, 25, 25), -1)
    cv2.addWeighted(tag_overlay, 0.85, frame, 0.15, 0, frame)
    cv2.rectangle(frame, (tag_x1, tag_y1), (tag_x2, tag_y2), box_color, 1)

    # Render Name
    cv2.putText(
        frame,
        name_text,
        (tag_x1 + 6, tag_y1 + nh + 4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        box_color,
        1,
        cv2.LINE_AA,
    )

    # Render Subtext / Distance
    cv2.putText(
        frame,
        sub_text,
        (tag_x1 + 6, tag_y1 + nh + sh + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (210, 210, 210),
        1,
        cv2.LINE_AA,
    )


def initialize_security_camera(camera_index: int = 0) -> cv2.VideoCapture:
    """
    Initializes laptop webcam with primary and secondary index fallbacks.
    """
    print(f"[INFO] Connecting to laptop webcam (device index {camera_index})...")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"[WARNING] Index {camera_index} unavailable. Trying index 1...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("\n" + "!" * 65, file=sys.stderr)
        print("CAMERA INITIALIZATION ERROR:", file=sys.stderr)
        print("Could not access laptop webcam. Please ensure:", file=sys.stderr)
        print("  1. No other application is using the webcam (Teams, Zoom, Browser).", file=sys.stderr)
        print("  2. Windows Camera privacy settings permit desktop apps.", file=sys.stderr)
        print("!" * 65 + "\n", file=sys.stderr)
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap


def run_security_system(
    camera_index: int = 0,
    db_path: str = DEFAULT_DB_PATH,
    threshold: float = DEFAULT_THRESHOLD,
    max_frames: int = 0,
    mock_image_path: str = None,
):
    """
    Runs the complete Smart Society Security System live application.
    """
    recognizer = SecurityRecognizer(db_path=db_path, threshold=threshold)
    print("\n" + "=" * 65)
    print("SMART SOCIETY SECURITY SYSTEM - LIVE ACCESS CONTROL")
    print("=" * 65)
    print(f"Database Path       : {db_path}")
    print(f"Registered Residents: {recognizer.resident_count}")
    print(f"Matching Threshold  : {recognizer.threshold:.2f}")
    print("-" * 65)
    print("CONTROLS:")
    print("  -> Press 'q' or [ESC] : Quit application")
    print("  -> Press '+' or '='   : Increase matching threshold (+0.02)")
    print("  -> Press '-' or '_'   : Decrease matching threshold (-0.02)")
    print("  -> Press 'r' or 'R'   : Reload residents from database")
    print("=" * 65 + "\n")

    is_mock = mock_image_path is not None
    cap = None

    if is_mock:
        mock_frame = cv2.imread(mock_image_path)
        if mock_frame is None:
            raise FileNotFoundError(f"Mock image file not found: {mock_image_path}")
    else:
        cap = initialize_security_camera(camera_index)
        if cap is None:
            return False

    window_name = "Smart Society Security System - Access Control"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    frame_count = 0
    fps = 0.0
    last_fps_time = time.time()

    try:
        while True:
            if is_mock:
                frame = mock_frame.copy()
                ret = True
                time.sleep(0.03)  # Simulate 30 FPS
            else:
                ret, frame = cap.read()

            if not ret or frame is None:
                print("[WARNING] Frame capture error.")
                break

            frame_count += 1
            if frame_count % 10 == 0:
                now = time.time()
                fps = 10.0 / max(now - last_fps_time, 1e-5)
                last_fps_time = now

            # Step 1: Process frame through recognizer
            face_results, gate_status = recognizer.process_frame(frame)

            # Step 2: Render each detected face's decision (Green/Red)
            for bbox, match_result in face_results:
                draw_face_decision(frame, bbox, match_result)

            # Step 3: Render Security HUD banner
            draw_security_hud(
                frame=frame,
                gate_status=gate_status,
                resident_count=recognizer.resident_count,
                threshold=recognizer.threshold,
                fps=fps,
                face_count=len(face_results),
            )

            # Step 4: Show frame in window
            cv2.imshow(window_name, frame)

            # Step 5: Handle user keyboard interactions
            key = cv2.waitKey(1) & 0xFF

            if key in [ord("q"), ord("Q"), 27]:  # 'q' or ESC
                print("\n[INFO] Exit command received. Shutting down system...")
                break

            elif key in [ord("+"), ord("=")]:  # Increase threshold
                new_t = round(recognizer.threshold + 0.02, 2)
                recognizer.set_threshold(new_t)
                print(f"[TUNING] Threshold increased to: {recognizer.threshold:.2f}")

            elif key in [ord("-"), ord("_")]:  # Decrease threshold
                new_t = round(recognizer.threshold - 0.02, 2)
                recognizer.set_threshold(new_t)
                print(f"[TUNING] Threshold decreased to: {recognizer.threshold:.2f}")

            elif key in [ord("r"), ord("R")]:  # Reload residents
                count = recognizer.reload_residents()
                print(f"[RELOAD] Database reloaded! Active residents: {count}")

            # Test limiter
            if 0 < max_frames <= frame_count:
                print(f"[INFO] Reached requested limit of {max_frames} frames. Exiting test.")
                break

    finally:
        if cap is not None:
            cap.release()
            print("[INFO] Camera device released.")
        cv2.destroyAllWindows()
        print("[INFO] OpenCV windows closed cleanly.")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Society Security System")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Matching threshold")
    parser.add_argument("--max-frames", type=int, default=0, help="Exit after N frames")
    parser.add_argument("--mock-image", type=str, default=None, help="Path to static image for testing")
    parser.add_argument("--db-path", type=str, default=DEFAULT_DB_PATH, help="Path to SQLite database")

    args = parser.parse_args()
    run_security_system(
        camera_index=args.camera,
        db_path=args.db_path,
        threshold=args.threshold,
        max_frames=args.max_frames,
        mock_image_path=args.mock_image,
    )
