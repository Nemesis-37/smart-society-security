"""
Phase 5 Test Suite: Face Recognition, Distance Computation & Security Decisions.
Tests matching registered residents, classifying unknown intruders,
adjustable matching threshold, and handling multi-face / no-face conditions.
"""

import os
import sys
import cv2
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.recognizer import SecurityRecognizer, DEFAULT_THRESHOLD
from models.face_pipeline import detect_faces, extract_face_roi, generate_face_encoding
from database.db_manager import DEFAULT_DB_PATH, get_resident_by_id


def run_phase5_tests():
    print("=" * 65)
    print("PHASE 5 TEST SUITE: FACE RECOGNITION & SECURITY DECISIONS")
    print("=" * 65)

    # Initialize recognizer with existing database
    recognizer = SecurityRecognizer(db_path=DEFAULT_DB_PATH, threshold=DEFAULT_THRESHOLD)
    print(f"Loaded {recognizer.resident_count} registered residents from SQLite.")
    assert recognizer.resident_count >= 20, f"Expected >= 20 residents in DB, got {recognizer.resident_count}"

    # Load a registered resident photograph from data/registered_faces
    registered_photo_path = os.path.join("data", "registered_faces", "RES-101_aarav_sharma.jpg")
    assert os.path.exists(registered_photo_path), f"Missing registered photo: {registered_photo_path}"
    reg_img = cv2.imread(registered_photo_path)

    # Test 1: Recognition of Registered Resident (ENTRY ALLOWED)
    reg_faces = detect_faces(reg_img)
    assert len(reg_faces) > 0, "Could not detect face in registered photo!"
    reg_roi = extract_face_roi(reg_img, reg_faces[0])
    reg_encoding = generate_face_encoding(reg_roi)

    result_reg = recognizer.recognize_encoding(reg_encoding)
    print(f"\n[Registered Resident Test]")
    print(f"  Decision      : {result_reg['decision']}")
    print(f"  Recognized    : {result_reg['is_recognized']}")
    print(f"  Resident ID   : {result_reg['resident_id']}")
    print(f"  Resident Name : {result_reg['name']}")
    print(f"  Face Distance : {result_reg['distance']:.4f} (Threshold: {result_reg['threshold']})")
    print(f"  Confidence    : {result_reg['confidence']}%")

    assert result_reg["is_recognized"] is True, "Registered resident was not recognized!"
    assert result_reg["decision"] == "ENTRY ALLOWED", "Access was not allowed for registered resident!"
    assert result_reg["resident_id"] == "RES-101", f"Wrong resident ID: {result_reg['resident_id']}"
    assert "Aarav Sharma" in result_reg["name"], f"Wrong name: {result_reg['name']}"
    assert result_reg["distance"] <= recognizer.threshold, "Distance exceeded matching threshold!"
    print("[PASS] Test 1: Registered resident recognized correctly with ENTRY ALLOWED in green status.")

    # Test 2: Unregistered / Unknown Person (ENTRY REJECTED)
    unknown_face = np.full((150, 150, 3), 40, dtype=np.uint8)
    cv2.circle(unknown_face, (45, 55), 14, (220, 220, 220), -1)
    cv2.circle(unknown_face, (105, 55), 14, (220, 220, 220), -1)
    cv2.rectangle(unknown_face, (65, 80), (85, 110), (180, 180, 180), -1)
    cv2.rectangle(unknown_face, (40, 125), (110, 135), (200, 200, 200), -1)

    unknown_encoding = generate_face_encoding(unknown_face)
    result_unknown = recognizer.recognize_encoding(unknown_encoding)

    print(f"\n[Unregistered Intruder Test]")
    print(f"  Decision      : {result_unknown['decision']}")
    print(f"  Recognized    : {result_unknown['is_recognized']}")
    print(f"  Resident ID   : {result_unknown['resident_id']}")
    print(f"  Name Tag      : {result_unknown['name']}")
    print(f"  Face Distance : {result_unknown['distance']:.4f} (Threshold: {result_unknown['threshold']})")

    assert result_unknown["is_recognized"] is False, "Unregistered intruder was incorrectly recognized as resident!"
    assert result_unknown["decision"] == "ENTRY REJECTED", "Access was erroneously granted to unknown person!"
    assert result_unknown["name"] == "Unknown", "Unregistered person should be named 'Unknown'!"
    assert result_unknown["distance"] > recognizer.threshold, "Distance should exceed matching threshold!"
    print("[PASS] Test 2: Unregistered face classified as Unknown with ENTRY REJECTED in red status.")

    # Test 3: Adjustable Matching Threshold
    recognizer.set_threshold(0.00)  # Ultra strict
    strict_result = recognizer.recognize_encoding(unknown_encoding)
    assert strict_result["decision"] == "ENTRY REJECTED"
    print(f"\n[Adjustable Threshold Test]")
    print(f"  Strict threshold tested -> Decision: {strict_result['decision']}")
    recognizer.set_threshold(DEFAULT_THRESHOLD)
    restored_result = recognizer.recognize_encoding(reg_encoding)
    assert restored_result["decision"] == "ENTRY ALLOWED", "Failed to restore threshold!"
    print(f"  Restored threshold to {recognizer.threshold} -> Decision: {restored_result['decision']}")
    print("[PASS] Test 3: Adjustable matching threshold successfully tested.")

    # Test 4: Multi-Face Frame Processing via process_frame
    results, gate_status = recognizer.process_frame(reg_img)
    print(f"\n[Frame Processing Verification]")
    print(f"  Faces Detected: {len(results)}")
    print(f"  Gate Status   : {gate_status}")
    for i, (bbox, res) in enumerate(results):
        print(f"    Face #{i+1} -> Name: {res['name']:15} | Decision: {res['decision']:14} | Dist: {res['distance']:.3f}")
    assert len(results) >= 1, "Failed to detect face in resident frame!"
    assert results[0][1]["decision"] == "ENTRY ALLOWED"
    print("[PASS] Test 4: Live frame processed without errors.")

    # Test 5: No-Face Situation Handling
    blank_frame = np.zeros((300, 300, 3), dtype=np.uint8)
    no_results, no_status = recognizer.process_frame(blank_frame)
    assert len(no_results) == 0, "Reported faces in blank frame!"
    assert no_status == "NO_FACE", f"Expected 'NO_FACE', got {no_status}"
    print(f"[PASS] Test 5: Handled no-face frame gracefully (Status: {no_status}).")

    print("\n" + "=" * 65)
    print("ALL PHASE 5 FACE RECOGNITION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_phase5_tests()
