"""
tests/test_evaluation.py
Phase 7 – Automated sanity tests for src/evaluate.py.
Verifies that the evaluation pipeline produces valid metric ranges and
creates the expected output files.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RESULTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "evaluation_results")
)


class TestEvaluation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run the full evaluation once and store metrics for all tests."""
        from src.evaluate import run_evaluation
        cls.metrics = run_evaluation()

    # ── Test 1: Metrics are in valid range ────────────────────────────────────
    def test_01_metric_ranges(self):
        for key in ("Accuracy", "Precision", "Recall", "F1_Score"):
            val = self.metrics[key]
            self.assertGreaterEqual(val, 0.0,   f"{key} < 0")
            self.assertLessEqual(val, 100.0,    f"{key} > 100")
        print(f"  PASS  All metrics in [0, 100] range.")

    # ── Test 2: Confusion matrix values are non-negative integers ─────────────
    def test_02_confusion_matrix_values(self):
        for key in ("TP", "TN", "FP", "FN"):
            self.assertGreaterEqual(self.metrics[key], 0, f"{key} < 0")
        total = self.metrics["TP"] + self.metrics["TN"] + self.metrics["FP"] + self.metrics["FN"]
        self.assertGreater(total, 0, "Total samples must be > 0")
        print(f"  PASS  TP={self.metrics['TP']}  TN={self.metrics['TN']}  "
              f"FP={self.metrics['FP']}  FN={self.metrics['FN']}  Total={total}")

    # ── Test 3: Output files exist ────────────────────────────────────────────
    def test_03_output_files_exist(self):
        expected_files = [
            "confusion_matrix.png",
            "environmental_robustness.png",
            "threshold_analysis.png",
            "evaluation_summary.txt",
            "test_results.csv",
        ]
        for fname in expected_files:
            path = os.path.join(RESULTS_DIR, fname)
            self.assertTrue(os.path.exists(path), f"Missing output file: {fname}")
        print(f"  PASS  All {len(expected_files)} output files exist.")

    # ── Test 4: Summary file contains metric values ───────────────────────────
    def test_04_summary_content(self):
        path = os.path.join(RESULTS_DIR, "evaluation_summary.txt")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Accuracy", content)
        self.assertIn("F1-Score", content)
        self.assertIn("CONFUSION MATRIX", content)
        print("  PASS  evaluation_summary.txt contains expected sections.")

    # ── Test 5: CSV has correct columns ──────────────────────────────────────
    def test_05_csv_structure(self):
        import csv
        path = os.path.join(RESULTS_DIR, "test_results.csv")
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
        expected = ["true_label", "predicted_label", "condition", "resident_id"]
        for col in expected:
            self.assertIn(col, headers, f"Missing CSV column: {col}")
        print("  PASS  test_results.csv has correct column headers.")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 7 – Evaluation Tests")
    print("=" * 60)
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromTestCase(TestEvaluation)
    runner  = unittest.TextTestRunner(verbosity=0)
    result  = runner.run(suite)
    print("=" * 60)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}  ERRORS: {len(result.errors)}")
    print("=" * 60)
