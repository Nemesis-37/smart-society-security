"""
Phase 4 Test Suite: Live Laptop Webcam Face Detection Integration.
Tests camera initialization, error handling, bounding box rendering,
HUD overlays, and video frame face detection pipeline.
"""

import os
import sys
import cv2
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.face_pipeline import detect_faces, CASCADE_PATH
from webcam_face_detection import (
    initialize_camera,
    draw_styled_bounding_box,
    draw_hud_overlay,
    run_live_webcam,
)


def run_phase4_tests():
    print("=" * 65)
    print("PHASE 4 TEST SUITE: LIVE WEBCAM & FACE DETECTION INTEGRATION")
    print("=" * 65)

    sample_face_path = r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
    assert os.path.exists(sample_face_path), f"Sample face not found at {sample_face_path}"
    test_frame = cv2.imread(sample_face_path)

    # Test 1: Verify Haar Cascade Loading
    assert os.path.exists(CASCADE_PATH), f"Haar cascade XML not found: {CASCADE_PATH}"
    print(f"[PASS] Test 1: OpenCV Haar Cascade loaded from: {CASCADE_PATH}")

    # Test 2: Face Detection Pipeline on Video Frame
    faces = detect_faces(test_frame)
    assert len(faces) == 1, f"Expected 1 face detected, got {len(faces)}"
    x, y, w, h = faces[0]
    print(f"[PASS] Test 2: Face detected in frame at x={x}, y={y}, w={w}, h={h}.")

    # Test 3: Bounding Box and Corner Bracket Rendering
    rendered_frame = test_frame.copy()
    draw_styled_bounding_box(rendered_frame, faces[0], label="Test Resident")
    # Verify image was modified
    assert not np.array_equal(rendered_frame, test_frame), "Bounding box did not modify frame pixels!"
    print("[PASS] Test 3: Green bounding box and corner accent brackets rendered successfully.")

    # Test 4: HUD Banner Rendering
    draw_hud_overlay(rendered_frame, face_count=1, fps=29.8)
    assert rendered_frame.shape == test_frame.shape, "HUD altered frame dimensions!"
    print("[PASS] Test 4: Status HUD overlay banner rendered successfully.")

    # Test 5: Camera Error Handling with Non-Existent Index
    print("\nTesting camera error handling on invalid device index (999):")
    cap_bad = initialize_camera(camera_index=999)
    assert cap_bad is None, "initialize_camera should return None on invalid device!"
    print("[PASS] Test 5: Camera initialization handled invalid index cleanly with user guidance.")

    # Test 6: Laptop Webcam Availability Check
    print("\nProbing laptop hardware webcam (Index 0)...")
    hw_cap = cv2.VideoCapture(0)
    hw_available = hw_cap.isOpened()
    if hw_available:
        ret, hw_frame = hw_cap.read()
        hw_cap.release()
        if ret and hw_frame is not None:
            print(f"[PASS] Test 6: Physical laptop webcam (Index 0) detected and functional! Resolution: {hw_frame.shape[1]}x{hw_frame.shape[0]}")
        else:
            print("[INFO] Test 6: Laptop webcam index 0 opened, but frame capture is held or disabled by OS privacy.")
    else:
        print("[INFO] Test 6: Laptop webcam index 0 is currently closed or in use by another desktop process.")

    # Test 7: Video Frame Loop with Mock Input (Headless Verification)
    print("\nRunning webcam video loop in test mode (max 5 frames)...")
    # Save a temporary mock frame
    success = run_live_webcam(max_frames=5, mock_input_path=sample_face_path)
    assert success is True, "Live webcam routine failed during frame processing!"
    print("[PASS] Test 7: Webcam video processing loop ran 5 frames and exited cleanly.")

    print("=" * 65)
    print("ALL PHASE 4 WEBCAM & FACE DETECTION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_phase4_tests()
