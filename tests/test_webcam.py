"""
tests/test_webcam.py
Phase 4 – Automated tests for webcam_detection.py.
All tests use static images or mocked objects; no live camera required.
"""

import os
import sys
import unittest
import numpy as np
import cv2

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.face_recognition import detect_faces
from src.webcam_detection import draw_bounding_box, draw_hud, initialize_camera

GRACE_PATH = (
    r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages"
    r"\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
)


class TestWebcamDetection(unittest.TestCase):

    # ── Test 1: Haar Cascade file exists ─────────────────────────────────────
    def test_01_cascade_file_exists(self):
        cascade_path = os.path.join(cv2.data.haarcascades,
                                    "haarcascade_frontalface_default.xml")
        self.assertTrue(os.path.exists(cascade_path),
                        f"Cascade file missing: {cascade_path}")
        print("  PASS  Haar Cascade file found.")

    # ── Test 2: Face detected in grace_hopper.jpg ────────────────────────────
    def test_02_face_detected_in_reference_image(self):
        self.assertTrue(os.path.exists(GRACE_PATH),
                        f"Reference image missing: {GRACE_PATH}")
        frame = cv2.imread(GRACE_PATH)
        self.assertIsNotNone(frame, "Could not load reference image.")
        faces = detect_faces(frame)
        self.assertGreater(len(faces), 0,
                           "Expected at least 1 face in grace_hopper.jpg")
        print(f"  PASS  {len(faces)} face(s) detected in reference image.")

    # ── Test 3: Bounding box rendering ───────────────────────────────────────
    def test_03_bounding_box_rendering(self):
        frame  = np.zeros((300, 400, 3), dtype=np.uint8)
        bbox   = (50, 50, 100, 100)
        result = draw_bounding_box(frame.copy(), bbox, color=(0, 255, 0))
        # At least some pixels changed (non-zero)
        self.assertTrue(np.any(result > 0), "No pixels were drawn.")
        print("  PASS  Bounding box rendered correctly.")

    # ── Test 4: HUD overlay rendering ────────────────────────────────────────
    def test_04_hud_overlay_rendering(self):
        frame  = np.zeros((480, 640, 3), dtype=np.uint8)
        result = draw_hud(frame.copy(), face_count=2, fps=30.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
        print("  PASS  HUD overlay applied without shape change.")

    # ── Test 5: Camera error handling (invalid index) ─────────────────────────
    def test_05_camera_error_handling(self):
        cap = initialize_camera(index=999)
        # Either returns None (no camera at index 999) or a valid cap
        # We just verify no exception is raised
        if cap is not None:
            cap.release()
        print("  PASS  Camera error handling did not raise an exception.")

    # ── Test 6: Mock video loop (5 frames, headless) ──────────────────────────
    def test_06_mock_video_loop(self):
        from src.webcam_detection import run_live_detection
        # Passes mock_image_path + max_frames>0 → headless, no window
        run_live_detection(mock_image_path=GRACE_PATH, max_frames=5)
        print("  PASS  Mock video loop completed 5 frames without error.")

    # ── Test 7: No-face blank frame returns 0 faces ───────────────────────────
    def test_07_no_face_blank_frame(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = detect_faces(blank)
        self.assertEqual(len(faces), 0,
                         f"Expected 0 faces on blank frame, got {len(faces)}")
        print("  PASS  Blank frame correctly returns 0 faces.")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4 – Webcam Detection Tests")
    print("=" * 60)
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromTestCase(TestWebcamDetection)
    runner  = unittest.TextTestRunner(verbosity=0)
    result  = runner.run(suite)
    print("=" * 60)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}  ERRORS: {len(result.errors)}")
    print("=" * 60)
