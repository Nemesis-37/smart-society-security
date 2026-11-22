"""
Phase 3 Test Suite: Resident Registration, Face Validation & 20+ Residents Verification.
"""

import os
import sys
import tempfile
import cv2
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import (
    init_db,
    get_all_residents,
    get_resident_count,
    get_resident_by_id,
    check_duplicate_id,
)
from models.face_pipeline import validate_photograph
from register_resident import register_from_image_array, register_from_file
from seed_residents import seed_residents, RESIDENT_PROFILES


def run_phase3_tests():
    print("=" * 65)
    print("PHASE 3 TEST SUITE: RESIDENT REGISTRATION & 20+ DATABASE VALIDATION")
    print("=" * 65)

    # Use isolated test database
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "phase3_test.db")
    init_db(test_db)

    sample_face_path = r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
    assert os.path.exists(sample_face_path), f"Sample face not found at {sample_face_path}"

    # Test 1: Photograph Validation on Valid Human Face
    valid, msg, enc, bbox = validate_photograph(sample_face_path)
    assert valid is True, f"Validation failed on valid human face: {msg}"
    assert enc is not None and enc.shape == (128,), f"Expected (128,) vector, got {enc.shape}"
    assert bbox is not None and len(bbox) == 4, f"Invalid bbox: {bbox}"
    print(f"[PASS] Test 1: Validated human face photograph successfully. Bounding box: {bbox}")

    # Test 2: Photograph Validation on Invalid Image (Blank image / No face)
    blank_img = np.zeros((200, 200, 3), dtype=np.uint8)
    valid_blank, msg_blank, enc_blank, bbox_blank = validate_photograph(blank_img)
    assert valid_blank is False, "Validation erroneously succeeded on blank image!"
    assert enc_blank is None, "Encoding was generated for non-existent face!"
    print(f"[PASS] Test 2: Successfully rejected invalid photograph without a face: '{msg_blank}'")

    # Test 3: Register Resident via Image File
    success, msg = register_from_file(
        image_path=sample_face_path,
        resident_id="RES-001",
        name="Dr. Grace Hopper",
        db_path=test_db,
    )
    assert success is True, f"Registration from file failed: {msg}"
    res = get_resident_by_id("RES-001", test_db)
    assert res is not None, "Registered resident not found in database!"
    assert res["name"] == "Dr. Grace Hopper", "Name mismatch!"
    assert res["face_encoding"].shape == (128,), "Face encoding shape mismatch!"
    print(f"[PASS] Test 3: Successfully registered resident 'Dr. Grace Hopper' (RES-001).")

    # Test 4: Prevent Duplicate Resident ID
    dup_success, dup_msg = register_from_file(
        image_path=sample_face_path,
        resident_id="RES-001",  # Same ID!
        name="Grace Duplicate",
        db_path=test_db,
    )
    assert dup_success is False, "Allowed duplicate resident ID registration!"
    assert "already exists" in dup_msg.lower(), f"Unexpected duplicate error message: {dup_msg}"
    print(f"[PASS] Test 4: Duplicate resident ID 'RES-001' detected and rejected: '{dup_msg}'")

    # Test 5: Rejection of Invalid Face during Registration
    bad_success, bad_msg = register_from_image_array(
        image=blank_img,
        resident_id="RES-002",
        name="No Face Resident",
        db_path=test_db,
    )
    assert bad_success is False, "Allowed registration of image without a face!"
    print(f"[PASS] Test 5: Registration correctly refused invalid image: '{bad_msg}'")

    # Test 6: Seed and Verify at least 20 Residents
    seed_count = seed_residents(db_path=test_db)
    assert seed_count >= 20, f"Expected at least 20 residents, seeded {seed_count}"
    
    all_res = get_all_residents(test_db)
    assert len(all_res) >= 20, f"Database holds {len(all_res)} residents, expected >= 20"
    print(f"[PASS] Test 6: Successfully verified {len(all_res)} registered residents in database.")
    
    # Print sample of registered residents
    print("-" * 65)
    print("Sample Registered Residents in SQLite:")
    for r in all_res[:5]:
        print(f"  -> ID: {r['resident_id']:8} | Name: {r['name']:20} | Encoding Shape: {r['face_encoding'].shape} | Date: {r['registration_date']}")
    print(f"  ... and {len(all_res) - 5} more residents verified.")

    # Cleanup temp db
    try:
        os.remove(test_db)
        os.rmdir(temp_dir)
    except Exception:
        pass

    print("=" * 65)
    print("ALL PHASE 3 REGISTRATION & DATABASE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_phase3_tests()
