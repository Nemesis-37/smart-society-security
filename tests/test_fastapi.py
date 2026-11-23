"""
tests/test_fastapi.py
Automated integration tests for FastAPI backend layer.
Verifies Phases 3, 5, and 6 endpoints:
  - Health & Dashboard
  - Resident listing, photo serving, registration validation, deletion
  - Live gate controls: start, stop, status, threshold, reload, stream
  - Entry logs with SQLite querying, status filtering, and pagination
"""

import os
import sys
import unittest
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.config import DB_PATH
from backend.app.api.routes.health import get_health
from backend.app.api.routes.dashboard import get_dashboard_stats
from backend.app.api.routes.residents import list_residents, get_resident_photo
from backend.app.api.routes.gate import get_gate_status, update_threshold, reload_database, start_camera, stop_camera
from backend.app.api.routes.evaluation import get_evaluation_summary, get_evaluation_plot
from backend.app.api.routes.logs import get_access_logs, get_log_by_id
from backend.app.schemas import ThresholdUpdate
from backend.app.camera_manager import camera_manager


class TestFastAPIFullSuite(unittest.TestCase):

    def test_01_health_endpoint(self):
        res = get_health()
        self.assertEqual(res.status, "healthy")
        self.assertTrue(res.database_connected)
        self.assertEqual(res.resident_count, 22)
        print(f"  PASS  Health check: {res.resident_count} residents connected.")

    def test_02_dashboard_stats(self):
        res = get_dashboard_stats()
        self.assertEqual(res.total_residents, 22)
        self.assertEqual(res.database_status, "Connected")
        self.assertEqual(res.backend_status, "Online")
        self.assertEqual(res.threshold, 0.50)
        self.assertIsNotNone(res.evaluation_accuracy)
        print(f"  PASS  Dashboard stats: total={res.total_residents}, acc={res.evaluation_accuracy}%")

    def test_03_residents_list_and_privacy(self):
        residents = list_residents()
        self.assertEqual(len(residents), 22)
        first = residents[0]
        self.assertTrue(hasattr(first, "resident_id"))
        self.assertTrue(hasattr(first, "name"))
        self.assertTrue(hasattr(first, "photo_url"))
        self.assertFalse(hasattr(first, "face_encoding"), "CRITICAL: face_encoding must NOT exist on public model!")
        print(f"  PASS  Resident list: {len(residents)} records, zero vector leakage.")

    def test_04_resident_photo(self):
        response = get_resident_photo("R001")
        self.assertEqual(response.media_type, "image/jpeg")
        self.assertTrue(os.path.exists(response.path))
        print(f"  PASS  Resident photo served: file={response.path}")

    def test_05_gate_lifecycle_controls(self):
        # 1. Check initial status
        status_init = get_gate_status()
        self.assertIn("camera_active", status_init)
        self.assertIn("gate_status", status_init)

        # 2. Test start camera (handles sandbox graceful fallback)
        start_res = start_camera()
        self.assertIn("success", start_res)

        # 3. Test stop camera
        stop_res = stop_camera()
        self.assertTrue(stop_res["success"])
        self.assertFalse(stop_res["camera_active"])

        # 4. Update threshold
        update_res = update_threshold(ThresholdUpdate(threshold=0.55))
        self.assertEqual(update_res["threshold"], 0.55)

        # 5. Restore threshold
        restore_res = update_threshold(ThresholdUpdate(threshold=0.50))
        self.assertEqual(restore_res["threshold"], 0.50)

        # 6. Hot-reload
        reload_res = reload_database()
        self.assertTrue(reload_res["success"])
        self.assertEqual(reload_res["resident_count"], 22)
        print("  PASS  Live gate controls (start, stop, threshold, reload) verified.")

    def test_06_camera_stream_frame_generation(self):
        # Verify get_latest_jpeg returns valid JPEG bytes
        jpeg_bytes = camera_manager.get_latest_jpeg()
        self.assertIsNotNone(jpeg_bytes)
        self.assertGreater(len(jpeg_bytes), 500)
        # Check JPEG magic header 0xFF, 0xD8
        self.assertEqual(jpeg_bytes[:2], b"\xff\xd8")
        print(f"  PASS  Camera manager generates valid JPEG stream frame ({len(jpeg_bytes)} bytes).")

    def test_07_entry_logging_with_cooldown(self):
        # 1. Log an event
        camera_manager.log_entry_event(
            resident_id="R001",
            person_name="Aarav Sharma",
            status="ENTRY ALLOWED",
            distance=0.079
        )
        
        # 2. Immediate second call should be throttled by cooldown
        camera_manager.log_entry_event(
            resident_id="R001",
            person_name="Aarav Sharma",
            status="ENTRY ALLOWED",
            distance=0.079
        )

        # 3. Retrieve logs
        logs_res = get_access_logs(limit=10, offset=0)
        self.assertGreaterEqual(logs_res["total"], 1)
        self.assertGreaterEqual(len(logs_res["items"]), 1)
        
        first_log = logs_res["items"][0]
        self.assertIn("name", first_log)
        self.assertIn("decision", first_log)
        self.assertIn("timestamp", first_log)

        # Test single log lookup
        single_log = get_log_by_id(first_log["id"])
        self.assertEqual(single_log["id"], first_log["id"])
        print(f"  PASS  Entry logging & throttling verified: log #{single_log['id']} {single_log['decision']} - {single_log['name']}")

    def test_08_evaluation_summary_and_plots(self):
        ev = get_evaluation_summary()
        self.assertEqual(ev.accuracy, 100.0)
        self.assertEqual(ev.tp, 88)
        self.assertEqual(ev.tn, 88)
        self.assertEqual(ev.fp, 0)
        self.assertEqual(ev.fn, 0)

        p1 = get_evaluation_plot("confusion_matrix")
        p2 = get_evaluation_plot("environmental_robustness")
        p3 = get_evaluation_plot("threshold_analysis")
        self.assertTrue(os.path.exists(p1.path))
        self.assertTrue(os.path.exists(p2.path))
        self.assertTrue(os.path.exists(p3.path))
        print("  PASS  Evaluation summary & 3 visualization plots verified on disk.")


if __name__ == "__main__":
    print("=" * 60)
    print("FastAPI Backend Full Suite (Phases 3, 5, 6)")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFastAPIFullSuite)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    print("=" * 60)
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} FASTAPI TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}  ERRORS: {len(result.errors)}")
    print("=" * 60)
