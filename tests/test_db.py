"""
Test Suite for Phase 2: Database Operations and Connectivity.
Tests initialization, insertion, duplicate prevention, retrieval, and encoding fidelity.
"""

import os
import sys
import tempfile
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import (
    init_db,
    insert_resident,
    get_all_residents,
    get_resident_by_id,
    check_duplicate_id,
    delete_resident,
    get_resident_count,
    serialize_encoding,
    deserialize_encoding,
)


def run_all_tests():
    print("=" * 65)
    print("PHASE 2: DATABASE CONNECTIVITY & CRUD OPERATIONS TEST SUITE")
    print("=" * 65)

    # Use a temporary database file for testing
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_society.db")
    print(f"Using isolated test database: {test_db_path}")

    # Test 1: Initialize Database
    init_db(test_db_path)
    assert os.path.exists(test_db_path), "Database file was not created!"
    print("[PASS] Test 1: Database initialized and tables created successfully.")

    # Test 2: Check Duplicate on Empty DB
    is_dup = check_duplicate_id("RES-001", test_db_path)
    assert is_dup is False, "Empty DB reported duplicate ID!"
    print("[PASS] Test 2: Duplicate check correctly returned False for non-existent ID.")

    # Test 3: Insert Resident with Simulated 128-D Face Encoding
    # 128-dimensional float32 vector (standard representation for face encodings)
    np.random.seed(42)
    sample_encoding_1 = np.random.randn(128).astype(np.float32)
    sample_encoding_1 /= np.linalg.norm(sample_encoding_1)  # L2 normalize

    success = insert_resident(
        resident_id="RES-001",
        name="Aarav Sharma",
        face_encoding=sample_encoding_1,
        registration_date="2026-11-21 10:00:00",
        db_path=test_db_path,
    )
    assert success is True, "Failed to insert resident RES-001!"
    print("[PASS] Test 3: Successfully inserted resident 'Aarav Sharma' (RES-001).")

    # Test 4: Retrieve Resident by ID & Verify Encoding Fidelity
    resident = get_resident_by_id("RES-001", test_db_path)
    assert resident is not None, "Could not find inserted resident RES-001!"
    assert resident["resident_id"] == "RES-001", "ID mismatch!"
    assert resident["name"] == "Aarav Sharma", "Name mismatch!"
    assert resident["registration_date"] == "2026-11-21 10:00:00", "Date mismatch!"
    
    # Check that retrieved face encoding matches the original with 100% precision
    assert isinstance(resident["face_encoding"], np.ndarray), "Face encoding is not a numpy array!"
    assert resident["face_encoding"].shape == (128,), f"Encoding shape is {resident['face_encoding'].shape}, expected (128,)!"
    np.testing.assert_allclose(resident["face_encoding"], sample_encoding_1, rtol=1e-6, err_msg="Encoding values altered during serialization!")
    print("[PASS] Test 4: Retrieved resident by ID with 100% exact face encoding fidelity.")

    # Test 5: Duplicate Prevention
    dup_insert = insert_resident(
        resident_id="RES-001",
        name="Aarav Duplicate",
        face_encoding=sample_encoding_1,
        db_path=test_db_path,
    )
    assert dup_insert is False, "Database allowed insertion of a duplicate resident ID!"
    assert check_duplicate_id("RES-001", test_db_path) is True, "Duplicate check failed to detect existing ID!"
    print("[PASS] Test 5: Duplicate resident_id 'RES-001' was successfully detected and rejected.")

    # Test 6: Insert Multiple Residents & Test get_all_residents
    sample_encoding_2 = np.random.randn(128).astype(np.float32)
    sample_encoding_2 /= np.linalg.norm(sample_encoding_2)

    sample_encoding_3 = np.random.randn(128).astype(np.float32)
    sample_encoding_3 /= np.linalg.norm(sample_encoding_3)

    insert_resident("RES-002", "Priya Patel", sample_encoding_2, "2026-11-21 10:15:00", test_db_path)
    insert_resident("RES-003", "Rohan Mehta", sample_encoding_3, "2026-11-21 10:30:00", test_db_path)

    all_residents = get_all_residents(test_db_path)
    assert len(all_residents) == 3, f"Expected 3 residents, found {len(all_residents)}!"
    assert get_resident_count(test_db_path) == 3, "Resident count mismatch!"
    print(f"[PASS] Test 6: Retrieved all residents. Total count: {len(all_residents)}.")
    for r in all_residents:
        print(f"       -> ID: {r['resident_id']} | Name: {r['name']:15} | Encoding Shape: {r['face_encoding'].shape} | Registered: {r['registration_date']}")

    # Test 7: Input Validation
    try:
        insert_resident("", "Invalid Resident", sample_encoding_1, db_path=test_db_path)
        assert False, "Allowed empty resident_id!"
    except ValueError:
        print("[PASS] Test 7a: Correctly rejected empty resident_id.")

    try:
        insert_resident("RES-999", "", sample_encoding_1, db_path=test_db_path)
        assert False, "Allowed empty resident name!"
    except ValueError:
        print("[PASS] Test 7b: Correctly rejected empty resident name.")

    try:
        insert_resident("RES-999", "No Encoding", None, db_path=test_db_path)
        assert False, "Allowed None face_encoding!"
    except ValueError:
        print("[PASS] Test 7c: Correctly rejected None face_encoding.")

    # Test 8: Deletion
    del_success = delete_resident("RES-003", test_db_path)
    assert del_success is True, "Failed to delete resident RES-003!"
    assert get_resident_by_id("RES-003", test_db_path) is None, "RES-003 still exists after deletion!"
    assert get_resident_count(test_db_path) == 2, "Resident count not decremented after deletion!"
    print("[PASS] Test 8: Successfully deleted resident RES-003. Remaining count: 2.")

    # Cleanup temp db
    try:
        os.remove(test_db_path)
        os.rmdir(temp_dir)
    except Exception:
        pass

    print("=" * 65)
    print("ALL PHASE 2 DATABASE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_all_tests()
