"""
src/recognition_engine.py
Phase 5 – Face Recognition and Resident Matching.

Loads registered residents from SQLite once, caches encodings in memory,
and compares live webcam face encodings against the cache using Euclidean
distance.  Provides a gate decision for each detected face.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple, Any

from src.database import get_all_residents
from src.face_recognition import (
    detect_faces,
    extract_face_roi,
    generate_face_encoding,
    calculate_face_distance,
)


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_THRESHOLD: float = 0.50   # Euclidean distance  ≤ threshold → MATCH
GATE_ALLOWED  = "ENTRY ALLOWED"
GATE_REJECTED = "ENTRY REJECTED"
GATE_IDLE     = "GATE IDLE"
GATE_NO_FACE  = "NO FACE"


# ──────────────────────────────────────────────────────────────────────────────
# SecurityRecognizer
# ──────────────────────────────────────────────────────────────────────────────

class SecurityRecognizer:
    """
    Resident matching engine.

    Loads all registered resident encodings from SQLite into memory once,
    avoiding a database round-trip for every video frame.

    Usage
    -----
    recognizer = SecurityRecognizer()
    result = recognizer.recognize_encoding(candidate_encoding)
    results, gate_status = recognizer.process_frame(bgr_frame)
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        self.db_path   = db_path
        self.threshold = threshold
        self._residents: List[Dict[str, Any]] = []
        self.reload_residents()

    # ── Resident cache ────────────────────────────────────────────────────────

    def reload_residents(self) -> int:
        """
        Hot-reloads the resident list from SQLite without restarting.
        Returns the number of residents loaded.
        Skips records with missing or corrupt encodings.
        """
        raw = get_all_residents(self.db_path)
        valid = []
        for r in raw:
            enc = r.get("face_encoding")
            if enc is None or not isinstance(enc, np.ndarray) or enc.size == 0:
                print(f"[Recognizer] Skipping {r.get('resident_id')} – invalid encoding.")
                continue
            valid.append(r)
        self._residents = valid
        print(f"[Recognizer] Loaded {len(self._residents)} resident(s) from database.")
        return len(self._residents)

    @property
    def resident_count(self) -> int:
        return len(self._residents)

    # ── Core matching ─────────────────────────────────────────────────────────

    def recognize_encoding(self, candidate_enc: np.ndarray) -> Dict[str, Any]:
        """
        Compares a single face encoding against all cached residents.

        Parameters
        ----------
        candidate_enc : 1-D float32 numpy array (128 dimensions).

        Returns
        -------
        dict with keys:
          decision      – GATE_ALLOWED or GATE_REJECTED
          is_recognized – bool
          resident_id   – matched ID or None
          name          – matched name or "Unknown"
          distance      – best Euclidean distance found
          confidence    – 1 - (distance / threshold), clamped [0, 1]
          threshold     – current threshold value
        """
        if candidate_enc is None or candidate_enc.size == 0:
            return self._unknown_result(distance=1.0)

        if not self._residents:
            return self._unknown_result(distance=1.0)

        best_dist  = float("inf")
        best_match: Optional[Dict[str, Any]] = None

        for resident in self._residents:
            try:
                d = calculate_face_distance(candidate_enc, resident["face_encoding"])
                if d < best_dist:
                    best_dist  = d
                    best_match = resident
            except Exception:
                continue

        if best_dist <= self.threshold and best_match is not None:
            conf = max(0.0, min(1.0, 1.0 - (best_dist / self.threshold)))
            return {
                "decision"     : GATE_ALLOWED,
                "is_recognized": True,
                "resident_id"  : best_match["resident_id"],
                "name"         : best_match["name"],
                "distance"     : round(best_dist, 4),
                "confidence"   : round(conf, 4),
                "threshold"    : self.threshold,
            }

        return self._unknown_result(distance=round(best_dist, 4))

    def _unknown_result(self, distance: float = 1.0) -> Dict[str, Any]:
        return {
            "decision"     : GATE_REJECTED,
            "is_recognized": False,
            "resident_id"  : None,
            "name"         : "Unknown",
            "distance"     : distance,
            "confidence"   : 0.0,
            "threshold"    : self.threshold,
        }

    # ── Frame-level processing ─────────────────────────────────────────────────

    def process_frame(
        self, frame: np.ndarray
    ) -> Tuple[List[Tuple[Tuple, Dict]], str]:
        """
        Detects all faces in a BGR frame and runs recognition on each.

        Returns
        -------
        (results, gate_status)
          results     – list of (bbox, recognition_dict) for each detected face
          gate_status – overall status string for the gate display
        """
        if frame is None or frame.size == 0:
            return [], GATE_NO_FACE

        bboxes = detect_faces(frame)

        if not bboxes:
            return [], GATE_NO_FACE

        results = []
        any_allowed = False

        for bbox in bboxes:
            roi = extract_face_roi(frame, bbox)
            try:
                enc = generate_face_encoding(roi)
                result = self.recognize_encoding(enc)
            except Exception as e:
                result = self._unknown_result()
                print(f"[Recognizer] Encoding error: {e}")

            results.append((bbox, result))
            if result["is_recognized"]:
                any_allowed = True

        gate_status = GATE_ALLOWED if any_allowed else GATE_REJECTED
        return results, gate_status
