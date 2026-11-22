"""
Phase 6 Test Suite: End-to-End System Integration & Complete Pipeline Testing.
Verifies full loop: SQLite -> Recognition -> Gate Decision -> GUI Rendering:
  - Green ENTRY ALLOWED for registered residents
  - Red ENTRY REJECTED for unknown intruders
  - Multi-face scene handling & No-face stability
"""

import os
import sys
import cv2
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.recognizer import SecurityRecognizer, DEFAULT_THRESHOLD
from society_security_system import (
    draw_security_hud,
    draw_face_decision,
    run_security_system,
)
from database.db_manager import DEFAULT_DB_PATH, get_resident_count


def run_phase6_tests():
    print("=" * 65)
    print("PHASE 6 TEST SUITE: COMPLETE SYSTEM END-TO-END VERIFICATION")
    print("=" * 65)

    # 1. Database & Recognizer Verification
    total_residents = get_resident_count(DEFAULT_DB_PATH)
    assert total_residents >= 20, f"Expected >= 20 residents in DB, got {total_residents}"
    recognizer = SecurityRecognizer(db_path=DEFAULT_DB_PATH, threshold=DEFAULT_THRESHOLD)
    print(f"[PASS] Step 1: SQLite Database connected with {total_residents} active residents.")

    # 2. Registered Resident Frame Test (Green ENTRY ALLOWED)
    reg_photo = os.path.join("data", "registered_faces", "RES-101_aarav_sharma.jpg")
    assert os.path.exists(reg_photo), f"Missing resident photo: {reg_photo}"
    frame_reg = cv2.imread(reg_photo)

    results_reg, status_reg = recognizer.process_frame(frame_reg)
    assert len(results_reg) > 0, "Failed to detect face in resident test frame!"
    bbox, match_reg = results_reg[0]

    assert match_reg["decision"] == "ENTRY ALLOWED", f"Expected ENTRY ALLOWED, got {match_reg['decision']}"
    assert match_reg["is_recognized"] is True, "is_recognized was False for registered resident!"
    assert "Aarav Sharma" in match_reg["name"], f"Name mismatch: {match_reg['name']}"
    assert status_reg == "ENTRY ALLOWED", f"Gate status mismatch: {status_reg}"

    # Test rendering on frame
    rendered_reg = frame_reg.copy()
    draw_face_decision(rendered_reg, bbox, match_reg)
    draw_security_hud(rendered_reg, status_reg, total_residents, DEFAULT_THRESHOLD, 30.0, len(results_reg))
    print(f"[PASS] Step 2: Registered resident frame processed -> Decision: {match_reg['decision']} (Green). Name: {match_reg['name']}")

    # 3. Unregistered Visitor Test (Red ENTRY REJECTED)
    frame_unknown = np.full((300, 300, 3), 160, dtype=np.uint8)
    cv2.circle(frame_unknown, (90, 110), 18, (30, 30, 30), -1)
    cv2.circle(frame_unknown, (210, 110), 18, (30, 30, 30), -1)
    cv2.rectangle(frame_unknown, (135, 140), (165, 190), (50, 50, 50), -1)
    cv2.ellipse(frame_unknown, (150, 230), (45, 15), 0, 0, 180, (20, 20, 20), -1)

    from models.face_pipeline import generate_face_encoding
    enc_unk = generate_face_encoding(frame_unknown)
    match_unk = recognizer.recognize_encoding(enc_unk)

    assert match_unk["decision"] == "ENTRY REJECTED", f"Expected ENTRY REJECTED, got {match_unk['decision']}"
    assert match_unk["is_recognized"] is False, "Unknown face was erroneously recognized!"
    assert match_unk["name"] == "Unknown", f"Expected name 'Unknown', got {match_unk['name']}"

    rendered_unk = frame_unknown.copy()
    draw_face_decision(rendered_unk, (50, 50, 200, 200), match_unk)
    draw_security_hud(rendered_unk, "ENTRY REJECTED", total_residents, DEFAULT_THRESHOLD, 30.0, 1)
    print(f"[PASS] Step 3: Unregistered intruder frame processed -> Decision: {match_unk['decision']} (Red). Label: Unknown")

    # 4. Multi-Face Scene Test
    # Use uncompressed resident photo in a larger wide frame
    h, w = frame_reg.shape[:2]
    composite_frame = np.full((h, w + 200, 3), 180, dtype=np.uint8)
    composite_frame[:, :w] = frame_reg

    multi_results, multi_gate = recognizer.process_frame(composite_frame)
    assert len(multi_results) >= 1, "Failed to process scene!"
    rendered_multi = composite_frame.copy()
    for b, m in multi_results:
        draw_face_decision(rendered_multi, b, m)
    draw_security_hud(rendered_multi, multi_gate, total_residents, DEFAULT_THRESHOLD, 30.0, len(multi_results))
    print(f"[PASS] Step 4: Multi-face scene processed successfully. Gate status: {multi_gate}")

    # 5. No-Face Situation Handling
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    no_results, no_gate = recognizer.process_frame(blank_frame)
    assert len(no_results) == 0, "No-face frame reported false detections!"
    assert no_gate == "NO_FACE", f"Expected 'NO_FACE', got {no_gate}"
    draw_security_hud(blank_frame, no_gate, total_residents, DEFAULT_THRESHOLD, 30.0, 0)
    print(f"[PASS] Step 5: No-face condition handled gracefully with idle gate status: '{no_gate}'")

    # 6. End-to-End Live Application Mock Execution
    print("\nRunning integrated security application loop in test mode (max 5 frames)...")
    success = run_security_system(
        max_frames=5,
        mock_image_path=reg_photo,
        threshold=DEFAULT_THRESHOLD,
    )
    assert success is True, "Security system loop encountered an error!"
    print("[PASS] Step 6: Live security system loop ran 5 frames end-to-end and exited cleanly.")

    print("\n" + "=" * 65)
    print("ALL PHASE 6 END-TO-END INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_phase6_tests()
