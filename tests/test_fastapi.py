"""
tests/test_fastapi.py
Automated integration tests for FastAPI backend layer.
Verifies all Phase 3 & Phase 4 endpoints: health, dashboard, residents, gate, evaluation, logs.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.api.routes.health import get_health
from backend.app.api.routes.dashboard import get_dashboard_stats
from backend.app.api.routes.residents import list_residents, get_resident_photo
from backend.app.api.routes.gate import get_gate_status, update_threshold, reload_database
from backend.app.api.routes.evaluation import get_evaluation_summary, get_evaluation_plot
from backend.app.api.routes.logs import get_access_logs
from backend.app.schemas import ThresholdUpdate


class TestFastAPIEndpoints(unittest.TestCase):

    def test_01_health_endpoint(self):
        res = get_health()
        self.assertEqual(res.status, "healthy")
        self.assertTrue(res.database_connected)
        self.assertEqual(res.resident_count, 22)
        print(f"  PASS  get_health(): status={res.status}, residents={res.resident_count}")

    def test_02_dashboard_stats(self):
        res = get_dashboard_stats()
        self.assertEqual(res.total_residents, 22)
        self.assertEqual(res.database_status, "Connected")
        self.assertEqual(res.backend_status, "Online")
        self.assertEqual(res.threshold, 0.50)
        self.assertIsNotNone(res.evaluation_accuracy)
        print(f"  PASS  get_dashboard_stats(): total={res.total_residents}, acc={res.evaluation_accuracy}%")

    def test_03_residents_list_and_privacy(self):
        residents = list_residents()
        self.assertEqual(len(residents), 22)
        first = residents[0]
        self.assertTrue(hasattr(first, "resident_id"))
        self.assertTrue(hasattr(first, "name"))
        self.assertTrue(hasattr(first, "photo_url"))
        self.assertFalse(hasattr(first, "face_encoding"), "CRITICAL: face_encoding must NOT exist on public model!")
        print(f"  PASS  list_residents(): {len(residents)} records, zero vector leakage.")

    def test_04_resident_photo(self):
        response = get_resident_photo("R001")
        self.assertEqual(response.media_type, "image/jpeg")
        self.assertTrue(os.path.exists(response.path))
        print(f"  PASS  get_resident_photo('R001'): file={response.path}")

    def test_05_gate_status_and_threshold(self):
        status = get_gate_status()
        self.assertEqual(status.status, "Active")
        self.assertEqual(status.resident_count, 22)

        # Update threshold
        update_res = update_threshold(ThresholdUpdate(threshold=0.55))
        self.assertEqual(update_res["threshold"], 0.55)

        # Restore threshold
        restore_res = update_threshold(ThresholdUpdate(threshold=0.50))
        self.assertEqual(restore_res["threshold"], 0.50)
        print("  PASS  gate_status and threshold update functional.")

    def test_06_gate_reload(self):
        reload_res = reload_database()
        self.assertTrue(reload_res["success"])
        self.assertEqual(reload_res["resident_count"], 22)
        print(f"  PASS  reload_database(): {reload_res['resident_count']} residents cached.")

    def test_07_evaluation_summary(self):
        ev = get_evaluation_summary()
        self.assertEqual(ev.accuracy, 100.0)
        self.assertEqual(ev.tp, 88)
        self.assertEqual(ev.tn, 88)
        self.assertEqual(ev.fp, 0)
        self.assertEqual(ev.fn, 0)
        print(f"  PASS  get_evaluation_summary(): acc={ev.accuracy}%, TP={ev.tp}, TN={ev.tn}")

    def test_08_evaluation_plots(self):
        p1 = get_evaluation_plot("confusion_matrix")
        p2 = get_evaluation_plot("environmental_robustness")
        p3 = get_evaluation_plot("threshold_analysis")
        self.assertTrue(os.path.exists(p1.path))
        self.assertTrue(os.path.exists(p2.path))
        self.assertTrue(os.path.exists(p3.path))
        print("  PASS  All 3 evaluation plots verified on disk.")

    def test_09_access_logs(self):
        logs = get_access_logs()
        self.assertEqual(logs, [])
        print("  PASS  get_access_logs(): clean empty list, no fabricated records.")


if __name__ == "__main__":
    print("=" * 60)
    print("FastAPI Backend Integration Test Suite")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIEndpoints)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    print("=" * 60)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} FASTAPI TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}  ERRORS: {len(result.errors)}")
    print("=" * 60)
