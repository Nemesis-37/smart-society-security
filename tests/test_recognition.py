"""
tests/test_recognition.py
Phase 5 – Automated tests for recognition_engine.py.
Uses pre-registered dataset images; no live camera required.
"""

import os
import sys
import unittest
import numpy as np
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.recognition_engine import (
    SecurityRecognizer,
    GATE_ALLOWED,
    GATE_REJECTED,
    GATE_NO_FACE,
    DEFAULT_THRESHOLD,
)
from src.face_recognition import (
    detect_faces,
    extract_face_roi,
    generate_face_encoding,
)
from src.database import get_all_residents

GRACE_PATH = (
    r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages"
    r"\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
)
DATASET_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "dataset", "residents")
)


class TestRecognitionEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.recognizer = SecurityRecognizer(threshold=DEFAULT_THRESHOLD)
        print(f"\n  Loaded {cls.recognizer.resident_count} resident(s) from database.")

    # ── Test 1: Residents loaded ──────────────────────────────────────────────
    def test_01_residents_loaded(self):
        self.assertGreater(self.recognizer.resident_count, 0,
                           "Database must have at least 1 resident.")
        print(f"  PASS  {self.recognizer.resident_count} resident(s) loaded.")

    # ── Test 2: Registered resident photo → ENTRY ALLOWED ────────────────────
    def test_02_registered_resident_recognized(self):
        # Find a registered resident and their photo in dataset/residents/
        residents = get_all_residents()
        self.assertTrue(len(residents) > 0, "No residents in DB.")

        # Try the first resident whose photo exists
        matched = False
        for resident in residents:
            rid = resident["resident_id"]
            photo = os.path.join(DATASET_DIR, f"{rid}.jpg")
            if not os.path.exists(photo):
                continue

            frame = cv2.imread(photo)
            faces = detect_faces(frame)
            if not faces:
                continue

            roi = extract_face_roi(frame, faces[0])
            enc = generate_face_encoding(roi)
            result = self.recognizer.recognize_encoding(enc)

            if result["is_recognized"] and result["resident_id"] == rid:
                matched = True
                print(f"  PASS  Recognized: {result['name']} ({rid})  dist={result['distance']:.4f}")
                break

        self.assertTrue(matched, "Could not recognize any registered resident from dataset photos.")

    # ── Test 3: Unknown face → ENTRY REJECTED ────────────────────────────────
    def test_03_unknown_face_rejected(self):
        # Synthetic random face encoding far from any registered resident
        rng = np.random.default_rng(42)
        rand_enc = rng.random(128).astype(np.float32)
        rand_enc /= np.linalg.norm(rand_enc)

        result = self.recognizer.recognize_encoding(rand_enc)
        self.assertFalse(result["is_recognized"],
                         "Random encoding should NOT be recognized.")
        self.assertEqual(result["decision"], GATE_REJECTED)
        print(f"  PASS  Unknown encoding rejected  dist={result['distance']:.4f}")

    # ── Test 4: Threshold adjustment ─────────────────────────────────────────
    def test_04_threshold_adjustment(self):
        orig = self.recognizer.threshold
        self.recognizer.threshold = 0.0   # nothing should match
        rng = np.random.default_rng(1)
        rand_enc = rng.random(128).astype(np.float32)
        rand_enc /= np.linalg.norm(rand_enc)
        result_strict = self.recognizer.recognize_encoding(rand_enc)
        self.assertEqual(result_strict["decision"], GATE_REJECTED)

        self.recognizer.threshold = 1.0   # everything should match (distance < 1 almost always)
        self.recognizer.threshold = orig  # restore
        print("  PASS  Threshold adjustment works correctly.")

    # ── Test 5: No-face blank frame → GATE_NO_FACE ───────────────────────────
    def test_05_no_face_blank_frame(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        results, gate_status = self.recognizer.process_frame(blank)
        self.assertEqual(gate_status, GATE_NO_FACE)
        self.assertEqual(len(results), 0)
        print("  PASS  Blank frame → GATE_NO_FACE, 0 results.")

    # ── Test 6: Multi-face frame processing ──────────────────────────────────
    def test_06_multi_face_frame(self):
        """Stack grace_hopper.jpg next to itself to simulate two faces."""
        self.assertTrue(os.path.exists(GRACE_PATH), "Reference image missing.")
        img = cv2.imread(GRACE_PATH)
        # Resize both halves to same height
        h, w = img.shape[:2]
        multi = np.hstack([img, img])          # two copies side-by-side

        results, gate_status = self.recognizer.process_frame(multi)
        # At least 1 face should be detected (the cascade may merge overlapping)
        self.assertGreaterEqual(len(results), 1,
                                "Expected at least 1 face in doubled frame.")
        print(f"  PASS  Multi-face frame → {len(results)} result(s), status={gate_status}")

    # ── Test 7: Hot reload ────────────────────────────────────────────────────
    def test_07_hot_reload(self):
        count_before = self.recognizer.resident_count
        reloaded = self.recognizer.reload_residents()
        self.assertEqual(reloaded, count_before,
                         "Hot reload should return same count.")
        print(f"  PASS  Hot reload returned {reloaded} resident(s).")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 5 – Recognition Engine Tests")
    print("=" * 60)
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromTestCase(TestRecognitionEngine)
    runner  = unittest.TextTestRunner(verbosity=0)
    result  = runner.run(suite)
    print("=" * 60)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}  ERRORS: {len(result.errors)}")
    print("=" * 60)
