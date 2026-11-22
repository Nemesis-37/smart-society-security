"""
Resident Registration CLI & Utility Module.
Supports capturing resident photographs via laptop webcam or uploading existing images,
validates face presence, extracts 128-d face encodings, and stores records in SQLite.
"""

import os
import sys
import cv2
import datetime
import numpy as np
from typing import Optional, Tuple

from database.db_manager import (
    init_db,
    insert_resident,
    check_duplicate_id,
    get_all_residents,
    get_resident_count,
    DEFAULT_DB_PATH,
)
from models.face_pipeline import (
    detect_faces,
    generate_face_encoding,
    validate_photograph,
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(DATA_DIR, "registered_faces")
os.makedirs(FACES_DIR, exist_ok=True)


def register_from_image_array(
    image: np.ndarray,
    resident_id: str,
    name: str,
    db_path: str = DEFAULT_DB_PATH,
) -> Tuple[bool, str]:
    """
    Validates a numpy image array, checks for duplicates, extracts encoding,
    saves the image file, and inserts the resident into the SQLite database.
    """
    clean_id = str(resident_id).strip().upper()
    clean_name = str(name).strip()

    if not clean_id:
        return False, "Registration error: Resident ID cannot be empty."
    if not clean_name:
        return False, "Registration error: Resident Name cannot be empty."

    # Step 1: Duplicate check
    if check_duplicate_id(clean_id, db_path):
        return False, f"Duplicate Error: Resident ID '{clean_id}' already exists in database."

    # Step 2: Validate photograph
    is_valid, msg, encoding, bbox = validate_photograph(image, strict_single_face=True)
    if not is_valid:
        return False, msg

    # Step 3: Save photo into registered_faces directory
    safe_name = clean_name.lower().replace(" ", "_")
    photo_filename = f"{clean_id}_{safe_name}.jpg"
    photo_path = os.path.join(FACES_DIR, photo_filename)
    cv2.imwrite(photo_path, image)

    # Step 4: Insert into SQLite database
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = insert_resident(
        resident_id=clean_id,
        name=clean_name,
        face_encoding=encoding,
        registration_date=now_str,
        db_path=db_path,
    )

    if inserted:
        return (
            True,
            f"Successfully registered resident '{clean_name}' (ID: {clean_id}). Photo saved to: {photo_filename}",
        )
    else:
        return False, "Failed to insert resident record into database."


def register_from_file(
    image_path: str,
    resident_id: str,
    name: str,
    db_path: str = DEFAULT_DB_PATH,
) -> Tuple[bool, str]:
    """
    Loads an image from disk and registers the resident.
    """
    if not os.path.exists(image_path):
        return False, f"File does not exist: {image_path}"

    img = cv2.imread(image_path)
    if img is None:
        return False, f"Could not decode image file: {image_path}"

    return register_from_image_array(img, resident_id, name, db_path)


def capture_and_register_from_webcam(
    resident_id: str,
    name: str,
    db_path: str = DEFAULT_DB_PATH,
    camera_index: int = 0,
) -> Tuple[bool, str]:
    """
    Opens the laptop webcam for live interactive photograph capture.
    Allows user to align their face, press 's' or SPACE to capture, and 'q' to cancel.
    """
    clean_id = str(resident_id).strip().upper()
    clean_name = str(name).strip()

    if not clean_id:
        return False, "Resident ID cannot be empty."
    if not clean_name:
        return False, "Resident Name cannot be empty."

    if check_duplicate_id(clean_id, db_path):
        return False, f"Duplicate Error: Resident ID '{clean_id}' already exists."

    print("\n[INFO] Initializing webcam for photo capture...")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        # Try alternate index
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            return (
                False,
                "Camera Initialization Error: Could not access laptop webcam (Index 0 or 1). "
                "Ensure no other app is using the camera.",
            )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("-" * 60)
    print("WEBCAM REGISTRATION CONTROLS:")
    print("  -> Press 's' or [SPACE] : Capture photo when face is inside the box")
    print("  -> Press 'q' or [ESC]   : Cancel registration")
    print("-" * 60)

    captured_frame = None
    window_title = f"Resident Registration - {clean_name} ({clean_id})"

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARNING] Failed to grab frame from camera.")
            continue

        display_frame = frame.copy()
        faces = detect_faces(display_frame)

        # Draw guidance UI
        cv2.putText(
            display_frame,
            f"Registering: {clean_name} ({clean_id})",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        if len(faces) == 0:
            status_text = "No face detected - Center your face"
            status_color = (0, 0, 255)  # Red
        elif len(faces) == 1:
            status_text = "Face detected! Press [SPACE] or 's' to Capture"
            status_color = (0, 255, 0)  # Green
            x, y, w, h = faces[0]
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), status_color, 2)
            cv2.putText(display_frame, "Ready for Registration", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
        else:
            status_text = f"Multiple faces ({len(faces)}) detected! Only 1 face allowed"
            status_color = (0, 165, 255)  # Orange
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), status_color, 2)

        cv2.putText(
            display_frame,
            status_text,
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            status_color,
            2,
        )
        cv2.putText(
            display_frame,
            "Press 's' to Save | 'q' to Cancel",
            (20, display_frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1,
        )

        cv2.imshow(window_title, display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key in [ord("s"), ord("S"), 32]:  # 's' or SPACE
            if len(faces) == 1:
                captured_frame = frame.copy()
                break
            else:
                print(f"[ALERT] Cannot capture: {status_text}")
        elif key in [ord("q"), ord("Q"), 27]:  # 'q' or ESC
            print("[INFO] Registration cancelled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured_frame is None:
        return False, "Registration cancelled or no valid frame captured."

    return register_from_image_array(captured_frame, clean_id, clean_name, db_path)


def interactive_menu():
    """
    Console menu for resident registration.
    """
    init_db()
    while True:
        print("\n" + "=" * 60)
        print("  SMART SOCIETY SECURITY SYSTEM - RESIDENT REGISTRATION")
        print("=" * 60)
        print("  1. Register Resident via Laptop Webcam")
        print("  2. Register Resident via Image File (Upload)")
        print("  3. View All Registered Residents")
        print("  4. Seed 22 Sample Residents (Batch Load)")
        print("  5. Exit")
        print("=" * 60)

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            res_id = input("Enter Resident ID (e.g. RES-201): ").strip()
            name = input("Enter Full Resident Name: ").strip()
            success, msg = capture_and_register_from_webcam(res_id, name)
            print("\nResult:", msg)

        elif choice == "2":
            res_id = input("Enter Resident ID (e.g. RES-201): ").strip()
            name = input("Enter Full Resident Name: ").strip()
            path = input("Enter Image File Path: ").strip().strip('"').strip("'")
            success, msg = register_from_file(path, res_id, name)
            print("\nResult:", msg)

        elif choice == "3":
            residents = get_all_residents()
            print(f"\nTotal Registered Residents: {len(residents)}")
            print("-" * 65)
            for r in residents:
                print(f"  ID: {r['resident_id']:8} | Name: {r['name']:22} | Registered: {r['registration_date']}")
            print("-" * 65)

        elif choice == "4":
            from seed_residents import seed_residents
            count = seed_residents()
            print(f"\nSeeding complete! Database now holds {count} residents.")

        elif choice == "5":
            print("\nExiting Registration System. Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice. Please select 1 through 5.")


if __name__ == "__main__":
    interactive_menu()
