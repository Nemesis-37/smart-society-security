"""
Smart Society Security System - Master Application Entry Point.
Provides a unified launcher for:
  1. Live Webcam Security Gate (Face Recognition & Access Decision)
  2. Resident Registration (Webcam Capture or Image Upload)
  3. Database Management & Resident Directory
  4. Full System Diagnostics & Verification
"""

import os
import sys
import argparse

from database.db_manager import init_db, get_resident_count, get_all_residents, DEFAULT_DB_PATH
from register_resident import interactive_menu
from society_security_system import run_security_system


def print_banner():
    print(r"""
  =============================================================
             SMART SOCIETY SECURITY SYSTEM 
               Face Recognition Access Control
  =============================================================
  Powered by Python, OpenCV & SQLite
    """)


def view_residents():
    residents = get_all_residents()
    print("\n" + "=" * 70)
    print(f"REGISTERED SOCIETY RESIDENTS DIRECTORY (Total: {len(residents)})")
    print("=" * 70)
    if not residents:
        print("  [INFO] No residents currently registered in the database.")
    else:
        print(f"  {'ID':<10} {'Name':<25} {'Encoding Vector':<18} {'Registered Date':<20}")
        print("  " + "-" * 68)
        for r in residents:
            enc_shape = f"Float32 {r['face_encoding'].shape}"
            print(f"  {r['resident_id']:<10} {r['name']:<25} {enc_shape:<18} {r['registration_date']:<20}")
    print("=" * 70 + "\n")


def run_diagnostics():
    print("\n[DIAGNOSTICS] Running complete verification test suite...")
    import tests.test_phase5 as t5
    import tests.test_phase6 as t6
    t5.run_phase5_tests()
    t6.run_phase6_tests()


def main():
    init_db()
    count = get_resident_count()

    # If database has fewer than 20 residents, offer auto-seed
    if count < 20:
        print(f"[NOTE] Database currently has {count} residents. Seeding 22 default residents...")
        from seed_residents import seed_residents
        seed_residents()
        count = get_resident_count()

    while True:
        print_banner()
        print(f"  Active Database  : {DEFAULT_DB_PATH}")
        print(f"  Total Residents  : {count}")
        print("-" * 63)
        print("  1. Launch Live Security Gate System (Webcam)")
        print("  2. Open Resident Registration System (Capture / Upload)")
        print("  3. View Registered Residents Directory")
        print("  4. Run Full System Diagnostics & End-to-End Tests")
        print("  5. Exit")
        print("=" * 63)

        choice = input("  Select an option (1-5): ").strip()

        if choice == "1":
            print("\n[LAUNCH] Starting live security camera interface...")
            run_security_system()
        elif choice == "2":
            interactive_menu()
            count = get_resident_count()
        elif choice == "3":
            view_residents()
        elif choice == "4":
            run_diagnostics()
        elif choice == "5":
            print("\nExiting Smart Society Security System. Goodbye!\n")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid option. Please enter a number between 1 and 5.\n")


if __name__ == "__main__":
    main()
