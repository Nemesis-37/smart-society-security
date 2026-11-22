"""
src/main.py
Master launcher for the Smart Society Security System.
Provides a text menu to access all phases.
"""

import os
import sys

# Project root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 60)
    print("     SMART SOCIETY SECURITY SYSTEM")
    print("     OpenCV Face Recognition – Python 3.13")
    print("=" * 60)


def main_menu():
    while True:
        clear()
        print_banner()
        print("\n  1. Register a New Resident  (Phase 3)")
        print("  2. Live Webcam – Face Detection  (Phase 4)")
        print("  3. Live Security Gate – Full Recognition  (Phase 6)")
        print("  4. Run Performance Evaluation  (Phase 7)")
        print("  5. View Registered Residents")
        print("  6. Run All Tests")
        print("  0. Exit")
        print()
        choice = input("  Enter choice: ").strip()

        if choice == "1":
            from src.register_faces import registration_cli
            registration_cli()

        elif choice == "2":
            from src.webcam_detection import run_live_detection
            run_live_detection()

        elif choice == "3":
            from src.security_gate import run_security_system
            run_security_system()

        elif choice == "4":
            from src.evaluate import run_evaluation
            run_evaluation()
            input("\n  Press Enter to return to menu…")

        elif choice == "5":
            from src.database import get_all_residents
            residents = get_all_residents()
            print(f"\n  {len(residents)} registered resident(s):\n")
            for r in residents:
                print(f"    {r['resident_id']:8s}  {r['name']}")
            input("\n  Press Enter to return to menu…")

        elif choice == "6":
            import subprocess
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            tests = [
                "tests/test_database.py",
                "tests/test_registration.py",
                "tests/test_webcam.py",
                "tests/test_recognition.py",
                "tests/test_security_gate.py",
            ]
            for t in tests:
                print(f"\n--- {t} ---")
                subprocess.run([sys.executable, "-u", t], cwd=root)
            input("\n  Press Enter to return to menu…")

        elif choice == "0":
            print("\n  Goodbye.\n")
            break
        else:
            input("  Invalid choice. Press Enter to try again…")


if __name__ == "__main__":
    main_menu()
