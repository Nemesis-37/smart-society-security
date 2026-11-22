"""
Phase 4: Live Laptop Webcam Face Detection Application.
Captures live frames from laptop webcam, detects faces using OpenCV,
draws bounding boxes, handles camera initialization errors, and provides
keyboard shortcut ('q' or ESC) to close cleanly.
"""

import sys
import time
import argparse
import cv2
import numpy as np
from models.face_pipeline import detect_faces


def draw_styled_bounding_box(image: np.ndarray, bbox: tuple, label: str = "Face Detected"):
    """
    Renders an aesthetically styled bounding box with corner brackets and label tag.
    """
    x, y, w, h = bbox
    color = (0, 255, 0)  # Green
    thickness = 2
    corner_len = int(min(w, h) * 0.2)

    # Main rectangle
    cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)

    # Stylish corner accents
    # Top-Left
    cv2.line(image, (x, y), (x + corner_len, y), color, thickness + 2)
    cv2.line(image, (x, y), (x, y + corner_len), color, thickness + 2)
    # Top-Right
    cv2.line(image, (x + w, y), (x + w - corner_len, y), color, thickness + 2)
    cv2.line(image, (x + w, y), (x + w, y + corner_len), color, thickness + 2)
    # Bottom-Left
    cv2.line(image, (x, y + h), (x + corner_len, y + h), color, thickness + 2)
    cv2.line(image, (x, y + h), (x, y + h - corner_len), color, thickness + 2)
    # Bottom-Right
    cv2.line(image, (x + w, y + h), (x + w - corner_len, y + h), color, thickness + 2)
    cv2.line(image, (x + w, y + h), (x + w, y + h - corner_len), color, thickness + 2)

    # Label background banner
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    label_w, label_h = label_size
    tag_y = max(y - 10, label_h + 5)
    cv2.rectangle(image, (x, tag_y - label_h - 4), (x + label_w + 10, tag_y + 4), color, -1)
    cv2.putText(
        image,
        label,
        (x + 5, tag_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),  # Black text over green
        1,
        cv2.LINE_AA,
    )


def draw_hud_overlay(frame: np.ndarray, face_count: int, fps: float):
    """
    Renders top status dashboard and keyboard shortcuts.
    """
    h, w, _ = frame.shape
    # Translucent HUD bar at top
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 55), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Title & Stats
    cv2.putText(
        frame,
        "SMART SOCIETY SECURITY - LIVE FACE DETECTION",
        (15, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 200),
        2,
        cv2.LINE_AA,
    )

    status_str = f"Faces Detected: {face_count} | FPS: {fps:.1f} | Press 'q' or [ESC] to Exit"
    cv2.putText(
        frame,
        status_str,
        (15, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )


def initialize_camera(camera_index: int = 0) -> cv2.VideoCapture:
    """
    Attempts to connect to the laptop webcam.
    Tries primary index, then fallback index 1.
    """
    print(f"[INFO] Connecting to laptop webcam (index {camera_index})...")
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"[WARNING] Camera index {camera_index} not available. Trying index 1...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        error_msg = (
            "\n" + "!" * 65 + "\n"
            "CAMERA INITIALIZATION ERROR:\n"
            "Unable to access laptop webcam.\n"
            "Troubleshooting steps:\n"
            "  1. Ensure no other application (Zoom, Teams, Chrome, Camera App) is using the webcam.\n"
            "  2. Check Windows Settings -> Privacy & Security -> Camera -> Allow desktop apps to access camera.\n"
            "  3. Check if physical camera privacy shutter is open.\n"
            + "!" * 65 + "\n"
        )
        print(error_msg, file=sys.stderr)
        return None

    # Set preferred resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap


def run_live_webcam(
    camera_index: int = 0,
    max_frames: int = 0,
    mock_input_path: str = None,
):
    """
    Main loop for live webcam face detection.
    
    Parameters:
        camera_index: Webcam device index (default: 0).
        max_frames: Max frames to process before exiting (0 = infinite until 'q').
        mock_input_path: Optional static image path for headless automated testing.
    """
    is_mock = mock_input_path is not None
    cap = None

    if is_mock:
        print(f"[INFO] Running in mock test mode with input: {mock_input_path}")
        mock_frame = cv2.imread(mock_input_path)
        if mock_frame is None:
            raise FileNotFoundError(f"Mock image not found: {mock_input_path}")
    else:
        cap = initialize_camera(camera_index)
        if cap is None:
            return False

    window_name = "Smart Society Security System - Live Face Detection (Press 'q' to Exit)"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    frame_count = 0
    fps = 0.0
    start_time = time.time()
    last_fps_time = start_time

    print("\n" + "=" * 60)
    print("LIVE WEBCAM FACE DETECTION ACTIVE")
    print("  -> Press 'q' or [ESC] on the video window to stop")
    print("=" * 60)

    try:
        while True:
            if is_mock:
                frame = mock_frame.copy()
                ret = True
                time.sleep(0.03)  # Simulate ~30 FPS
            else:
                ret, frame = cap.read()

            if not ret or frame is None:
                print("[WARNING] Could not read video frame.")
                break

            frame_count += 1

            # Calculate FPS every 10 frames
            if frame_count % 10 == 0:
                now = time.time()
                fps = 10.0 / max(now - last_fps_time, 1e-5)
                last_fps_time = now

            # Step 1: Detect faces
            faces = detect_faces(frame)

            # Step 2: Draw bounding boxes
            for i, bbox in enumerate(faces):
                label = f"Face #{i + 1} ({bbox[2]}x{bbox[3]})"
                draw_styled_bounding_box(frame, bbox, label=label)

            # Step 3: Draw HUD
            draw_hud_overlay(frame, face_count=len(faces), fps=fps)

            # Step 4: Display frame
            cv2.imshow(window_name, frame)

            # Step 5: Check exit keys ('q', 'Q', ESC)
            key = cv2.waitKey(1) & 0xFF
            if key in [ord("q"), ord("Q"), 27]:
                print("\n[INFO] Exit key pressed ('q' / ESC). Shutting down video stream...")
                break

            # Limit frames if max_frames is set (for testing)
            if 0 < max_frames <= frame_count:
                print(f"\n[INFO] Reached requested test limit of {max_frames} frames.")
                break

    finally:
        if cap is not None:
            cap.release()
            print("[INFO] Camera device released successfully.")
        cv2.destroyAllWindows()
        print("[INFO] OpenCV windows closed cleanly.")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Laptop Webcam Face Detection (Phase 4)")
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default: 0)")
    parser.add_argument("--max-frames", type=int, default=0, help="Exit after N frames (default: 0 = infinite)")
    parser.add_argument("--mock-image", type=str, default=None, help="Path to static image for testing")

    args = parser.parse_args()
    run_live_webcam(
        camera_index=args.camera,
        max_frames=args.max_frames,
        mock_input_path=args.mock_image,
    )
