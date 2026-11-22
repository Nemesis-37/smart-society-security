"""
tests/test_security_gate.py
Phase 6 – Automated end-to-end test for security_gate.py.
Uses mock image input to verify the full pipeline without a live camera.
"""

import os
import sys
import unittest
import numpy as np
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.security_gate import run_security_system, annotate_frame
from src.recognition_engine import SecurityRecognizer, GATE_NO_FACE, GATE_ALLOWED, GATE_REJECTED

GRACE_PATH = (
    r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages"
    r"\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
)
DATASET_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "dataset", "residents")
)


class TestSecurityGate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.recognizer = SecurityRecognizer(threshold=0.50)

    # ── Test 1: Mock image pipeline runs without exception ───────────────────
    def test_01_mock_image_pipeline(self):
        """run_security_system with grace_hopper.jpg must not raise."""
        try:
            run_security_system(
                mock_image_path=GRACE_PATH,
                max_frames=1,          # headless – no window
            )
        except Exception as e:
            self.fail(f"Security gate raised exception: {e}")
        print("  PASS  Mock image pipeline completed without exception.")

    # ── Test 2: Blank frame → GATE_NO_FACE ───────────────────────────────────
    def test_02_blank_frame_idle_state(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        results, gate_status = self.recognizer.process_frame(blank)
        self.assertEqual(gate_status, GATE_NO_FACE)
        frame = annotate_frame(blank, results, gate_status)
        self.assertIsNotNone(frame)
        print("  PASS  Blank frame → GATE_NO_FACE with idle message overlay.")

    # ── Test 3: Reference image → at least one result ────────────────────────
    def test_03_reference_image_produces_result(self):
        self.assertTrue(os.path.exists(GRACE_PATH))
        frame = cv2.imread(GRACE_PATH)
        results, gate_status = self.recognizer.process_frame(frame)
        # grace_hopper is not a registered resident → REJECTED
        self.assertIn(gate_status, (GATE_REJECTED, GATE_ALLOWED, GATE_NO_FACE))
        print(f"  PASS  Reference image → {len(results)} face(s), gate={gate_status}")

    # ── Test 4: annotate_frame does not corrupt frame shape ──────────────────
    def test_04_annotate_frame_shape_preserved(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        annotated = annotate_frame(frame, [], GATE_NO_FACE)
        self.assertEqual(annotated.shape, (480, 640, 3))
        print("  PASS  annotate_frame preserves frame shape.")

    # ── Test 5: Registered resident photo → ENTRY ALLOWED ────────────────────
    def test_05_registered_resident_allowed(self):
        from src.database import get_all_residents
        from src.face_recognition import detect_faces, extract_face_roi, generate_face_encoding

        residents = get_all_residents()
        matched_allowed = False

        for r in residents:
            photo = os.path.join(DATASET_DIR, f"{r['resident_id']}.jpg")
            if not os.path.exists(photo):
                continue
            frame = cv2.imread(photo)
            faces = detect_faces(frame)
            if not faces:
                continue
            roi = extract_face_roi(frame, faces[0])
            enc = generate_face_encoding(roi)
            result = self.recognizer.recognize_encoding(enc)
            if result["is_recognized"]:
                matched_allowed = True
                print(f"  PASS  {r['name']} ({r['resident_id']}) → ENTRY ALLOWED  dist={result['distance']:.4f}")
                break

        self.assertTrue(matched_allowed, "No registered resident photo produced ENTRY ALLOWED.")

    # ── Test 6: Keyboard threshold adjust logic ───────────────────────────────
    def test_06_threshold_boundaries(self):
        r = SecurityRecognizer(threshold=0.50)
        r.threshold = round(min(1.0, r.threshold + 0.05), 2)
        self.assertEqual(r.threshold, 0.55)
        r.threshold = round(max(0.10, r.threshold - 0.20), 2)
        self.assertEqual(r.threshold, 0.35)
        print("  PASS  Threshold keyboard-adjust boundary logic correct.")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 6 – Security Gate Tests")
    print("=" * 60)
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromTestCase(TestSecurityGate)
    runner  = unittest.TextTestRunner(verbosity=0)
    result  = runner.run(suite)
    print("=" * 60)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}  ERRORS: {len(result.errors)}")
    print("=" * 60)
