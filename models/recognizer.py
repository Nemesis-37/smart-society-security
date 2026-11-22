"""
Face Recognition & Access Control Decision Engine.
Compares detected face encodings against the registered residents in SQLite,
computes Euclidean face distance, applies an adjustable matching threshold,
and determines security access decisions (ENTRY ALLOWED vs ENTRY REJECTED).
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from database.db_manager import get_all_residents, DEFAULT_DB_PATH
from models.face_pipeline import (
    detect_faces,
    extract_face_roi,
    generate_face_encoding,
    calculate_face_distance,
)

DEFAULT_THRESHOLD = 0.50


class SecurityRecognizer:
    def __init__(self, db_path: str = DEFAULT_DB_PATH, threshold: float = DEFAULT_THRESHOLD):
        """
        Initializes the security recognizer and loads all registered residents from SQLite.
        """
        self.db_path = db_path
        self.threshold = float(threshold)
        self.known_residents: List[Dict[str, Any]] = []
        self.known_encodings: List[np.ndarray] = []
        self.reload_residents()

    def reload_residents(self) -> int:
        """
        Refreshes the internal cache of registered residents and their encodings from SQLite.
        Returns the number of loaded residents.
        """
        all_records = get_all_residents(self.db_path)
        self.known_residents = all_records
        self.known_encodings = [r["face_encoding"] for r in all_records]
        return len(self.known_residents)

    @property
    def resident_count(self) -> int:
        return len(self.known_residents)

    def set_threshold(self, new_threshold: float):
        """
        Adjusts the matching threshold.
        """
        self.threshold = max(0.10, min(1.00, float(new_threshold)))

    def recognize_encoding(self, candidate_encoding: np.ndarray) -> Dict[str, Any]:
        """
        Compares a single 128-D candidate face encoding against all registered resident encodings.
        """
        if candidate_encoding is None or len(candidate_encoding) == 0:
            return {
                "decision": "ENTRY REJECTED",
                "is_recognized": False,
                "resident_id": None,
                "name": "Unknown",
                "distance": 999.0,
                "confidence": 0.0,
                "threshold": self.threshold,
            }

        if not self.known_encodings:
            return {
                "decision": "ENTRY REJECTED",
                "is_recognized": False,
                "resident_id": None,
                "name": "Unknown (No Database Records)",
                "distance": 999.0,
                "confidence": 0.0,
                "threshold": self.threshold,
            }

        distances = [
            calculate_face_distance(candidate_encoding, known_enc)
            for known_enc in self.known_encodings
        ]

        min_idx = int(np.argmin(distances))
        best_distance = float(distances[min_idx])
        matched_resident = self.known_residents[min_idx]

        if best_distance <= self.threshold:
            confidence = 100.0 - (best_distance / self.threshold) * 50.0
        else:
            confidence = max(0.0, 50.0 - ((best_distance - self.threshold) / self.threshold) * 50.0)

        if best_distance <= self.threshold:
            return {
                "decision": "ENTRY ALLOWED",
                "is_recognized": True,
                "resident_id": matched_resident["resident_id"],
                "name": matched_resident["name"],
                "distance": best_distance,
                "confidence": round(confidence, 1),
                "threshold": self.threshold,
            }
        else:
            return {
                "decision": "ENTRY REJECTED",
                "is_recognized": False,
                "resident_id": None,
                "name": "Unknown",
                "distance": best_distance,
                "confidence": round(confidence, 1),
                "threshold": self.threshold,
            }

    def process_frame(
        self, frame: np.ndarray
    ) -> Tuple[List[Tuple[Tuple[int, int, int, int], Dict[str, Any]]], str]:
        """
        Detects and recognizes all faces present in a single video frame.
        """
        if frame is None or frame.size == 0:
            return [], "NO_FACE"

        faces = detect_faces(frame)
        if not faces:
            return [], "NO_FACE"

        results = []
        any_rejected = False
        all_allowed = True

        for bbox in faces:
            face_roi = extract_face_roi(frame, bbox)
            try:
                cand_encoding = generate_face_encoding(face_roi)
                match_result = self.recognize_encoding(cand_encoding)
            except Exception:
                match_result = {
                    "decision": "ENTRY REJECTED",
                    "is_recognized": False,
                    "resident_id": None,
                    "name": "Unknown",
                    "distance": 999.0,
                    "confidence": 0.0,
                    "threshold": self.threshold,
                }

            if match_result["decision"] == "ENTRY REJECTED":
                any_rejected = True
                all_allowed = False

            results.append((bbox, match_result))

        if any_rejected:
            overall_status = "ENTRY REJECTED"
        elif all_allowed:
            overall_status = "ENTRY ALLOWED"
        else:
            overall_status = "NO_FACE"

        return results, overall_status
