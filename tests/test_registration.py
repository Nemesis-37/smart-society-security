"""
tests/test_registration.py
Phase 3 Test Suite: Resident Registration, Face Validation & Dataset Verification.
"""

import os
import sys
import tempfile
import cv2
import numpy as np

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.database import initialize_database, get_all_residents, get_resident_by_id
from src.face_recognition import validate_resident_photograph
from src.register_faces import register_resident_image, seed_20_residents, RESIDENTS_DIR


def run_registration_tests():
    print("=" * 65)
    print("PHASE 3: RESIDENT REGISTRATION & VALIDATION TEST SUITE")
    print("=" * 65)

    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "test_phase3_reg.db")
    initialize_database(test_db)

    sample_portrait = r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
    assert os.path.exists(sample_portrait), f"Sample portrait missing at: {sample_portrait}"
    valid_img = cv2.imread(sample_portrait)

    # Test 1: Successful Registration
    success, msg = register_resident_image(valid_img, "R001", "Aarav Sharma", db_path=test_db)
    assert success is True, f"Failed valid registration: {msg}"
    res = get_resident_by_id("R001", test_db)
    assert res is not None, "Registered resident not in database!"
    assert res["name"] == "Aarav Sharma", "Name mismatch!"
    assert res["face_encoding"].shape == (128,), "Face vector shape mismatch!"
    photo_path = os.path.join(RESIDENTS_DIR, "R001.jpg")
    assert os.path.exists(photo_path), f"Photograph not saved to {photo_path}"
    print(f"[PASS] Test 1: Resident 'Aarav Sharma' (R001) registered successfully. Photo saved to: {photo_path}")

    # Test 2: Duplicate Resident ID Rejection
    dup_ok, dup_msg = register_resident_image(valid_img, "R001", "Duplicate Person", db_path=test_db)
    assert dup_ok is False, "Allowed duplicate Resident ID registration!"
    assert "already exists" in dup_msg.lower(), f"Unexpected duplicate message: {dup_msg}"
    print(f"[PASS] Test 2: Duplicate Resident ID 'R001' detected and rejected: '{dup_msg}'")

    # Test 3: Invalid Photograph - No Face Detected
    blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    no_face_ok, no_face_msg = register_resident_image(blank_img, "R002", "Blank Face", db_path=test_db)
    assert no_face_ok is False, "Allowed registration of blank image without a face!"
    assert "no face" in no_face_msg.lower(), f"Unexpected message: {no_face_msg}"
    print(f"[PASS] Test 3: Blank image correctly rejected: '{no_face_msg}'")

    # Test 4: Multiple Faces Detected
    # Create composite frame with two adjacent faces
    h, w = valid_img.shape[:2]
    multi_img = np.zeros((h, w * 2, 3), dtype=np.uint8)
    multi_img[:, :w] = valid_img
    multi_img[:, w:] = valid_img
    multi_ok, multi_msg = register_resident_image(multi_img, "R003", "Two People", db_path=test_db)
    assert multi_ok is False, "Allowed registration of image containing multiple faces!"
    assert "multiple faces" in multi_msg.lower(), f"Unexpected message: {multi_msg}"
    print(f"[PASS] Test 4: Multi-face image correctly rejected: '{multi_msg}'")

    # Test 5: Seed and Verify 20+ Residents
    total_seeded = seed_20_residents(db_path=test_db)
    assert total_seeded >= 20, f"Expected >= 20 residents, got {total_seeded}"
    all_res = get_all_residents(test_db)
    assert len(all_res) >= 20, "Retrieved resident count less than 20!"
    print(f"[PASS] Test 5: Successfully seeded and verified {len(all_res)} residents in database.")
    
    # Check that photos exist in dataset/residents/
    missing_photos = []
    for r in all_res:
        p = os.path.join(RESIDENTS_DIR, f"{r['resident_id']}.jpg")
        if not os.path.exists(p):
            missing_photos.append(p)
    assert len(missing_photos) == 0, f"Missing photographs in dataset/residents: {missing_photos}"
    print(f"[PASS] Test 6: Verified all {len(all_res)} resident photographs exist in dataset/residents/.")

    # Cleanup temp db
    try:
        os.remove(test_db)
        os.rmdir(temp_dir)
    except Exception:
        pass

    print("=" * 65)
    print("ALL PHASE 3 REGISTRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_registration_tests()
