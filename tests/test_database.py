"""
tests/test_database.py
Phase 2 Test Suite: SQLite Database Connectivity & CRUD Verification.
"""

import os
import sys
import tempfile
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import (
    initialize_database,
    add_resident,
    get_all_residents,
    get_resident_by_id,
    delete_resident,
    check_duplicate_resident,
)


def run_database_tests():
    print("=" * 65)
    print("PHASE 2: SQLITE DATABASE VERIFICATION TEST SUITE")
    print("=" * 65)

    # Use an isolated temporary database file
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "test_society_phase2.db")
    print(f"Isolated Test Database: {test_db}")

    # Test 1: Database Initialization
    initialize_database(test_db)
    assert os.path.exists(test_db), "Database file was not created!"
    print("[PASS] Test 1: Database schema initialized successfully.")

    # Test 2: Check Duplicate on Empty Database
    assert check_duplicate_resident("R001", test_db) is False, "Empty DB returned True for duplicate!"
    print("[PASS] Test 2: Duplicate check correctly returned False for non-existent ID.")

    # Test 3: Insert Resident with 128-D Face Encoding
    np.random.seed(42)
    sample_enc_1 = np.random.randn(128).astype(np.float32)
    sample_enc_1 /= np.linalg.norm(sample_enc_1)

    success = add_resident(
        resident_id="R001",
        name="Aarav Sharma",
        face_encoding=sample_enc_1,
        registration_date="2026-11-22 10:00:00",
        db_path=test_db,
    )
    assert success is True, "Failed to insert resident R001!"
    print("[PASS] Test 3: Resident 'Aarav Sharma' (R001) inserted successfully.")

    # Test 4: Retrieve Resident by ID & Check Encoding Fidelity
    resident = get_resident_by_id("R001", test_db)
    assert resident is not None, "Failed to retrieve resident R001!"
    assert resident["resident_id"] == "R001", "Resident ID mismatch!"
    assert resident["name"] == "Aarav Sharma", "Name mismatch!"
    assert resident["face_encoding"].shape == (128,), f"Encoding shape is {resident['face_encoding'].shape}"
    np.testing.assert_allclose(resident["face_encoding"], sample_enc_1, rtol=1e-6)
    print("[PASS] Test 4: Retrieved resident by ID with 100% exact vector fidelity.")

    # Test 5: Prevent Duplicate Resident ID
    dup_success = add_resident(
        resident_id="R001",
        name="Duplicate Aarav",
        face_encoding=sample_enc_1,
        db_path=test_db,
    )
    assert dup_success is False, "Database allowed duplicate resident ID insertion!"
    assert check_duplicate_resident("R001", test_db) is True, "check_duplicate_resident failed to find R001!"
    print("[PASS] Test 5: Duplicate resident ID 'R001' detected and rejected.")

    # Test 6: Insert Multiple & get_all_residents
    sample_enc_2 = np.random.randn(128).astype(np.float32)
    sample_enc_2 /= np.linalg.norm(sample_enc_2)
    add_resident("R002", "Priya Patel", sample_enc_2, db_path=test_db)

    all_residents = get_all_residents(test_db)
    assert len(all_residents) == 2, f"Expected 2 residents, got {len(all_residents)}"
    print(f"[PASS] Test 6: Retrieved all residents successfully (Total: {len(all_residents)}).")
    for r in all_residents:
        print(f"       -> ID: {r['resident_id']} | Name: {r['name']:15} | Vector: {r['face_encoding'].shape}")

    # Test 7: Delete Resident
    del_res = delete_resident("R002", test_db)
    assert del_res is True, "Failed to delete resident R002!"
    assert get_resident_by_id("R002", test_db) is None, "R002 still present after deletion!"
    assert len(get_all_residents(test_db)) == 1, "Resident count not decremented!"
    print("[PASS] Test 7: Resident R002 deleted successfully. Remaining count: 1.")

    # Cleanup temp db
    try:
        os.remove(test_db)
        os.rmdir(temp_dir)
    except Exception:
        pass

    print("=" * 65)
    print("ALL PHASE 2 DATABASE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_database_tests()
