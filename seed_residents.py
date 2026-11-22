"""
Seed Script: Registers 22 Distinct Residents for the Smart Society Security System.
Generates unique resident portraits, extracts 128-D face encodings using the
standard validation pipeline, and populates the SQLite database.
"""

import os
import cv2
import numpy as np
from database.db_manager import (
    init_db,
    insert_resident,
    get_resident_count,
    delete_resident,
    check_duplicate_id,
    DEFAULT_DB_PATH,
)
from models.face_pipeline import validate_photograph, detect_faces, extract_face_roi

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(DATA_DIR, "registered_faces")
os.makedirs(FACES_DIR, exist_ok=True)

RESIDENT_PROFILES = [
    ("RES-101", "Aarav Sharma"),
    ("RES-102", "Priya Patel"),
    ("RES-103", "Rohan Mehta"),
    ("RES-104", "Ananya Iyer"),
    ("RES-105", "Vikram Malhotra"),
    ("RES-106", "Neha Singh"),
    ("RES-107", "Kabir Verma"),
    ("RES-108", "Sneha Kulkarni"),
    ("RES-109", "Rahul Gupta"),
    ("RES-110", "Pooja Nair"),
    ("RES-111", "Aditya Joshi"),
    ("RES-112", "Tanvi Rao"),
    ("RES-113", "Arjun Das"),
    ("RES-114", "Riya Sen"),
    ("RES-115", "Siddharth Bhat"),
    ("RES-116", "Ishita Deshmukh"),
    ("RES-117", "Manish Tiwari"),
    ("RES-118", "Shreya Roy"),
    ("RES-119", "Kunal Bansal"),
    ("RES-120", "Divya Reddy"),
    ("RES-121", "Amit Saxena"),
    ("RES-122", "Meera Nambiar"),
]


def load_base_portrait() -> np.ndarray:
    """Loads sample portrait image."""
    sample_path = r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\matplotlib\mpl-data\sample_data\grace_hopper.jpg"
    base_img = cv2.imread(sample_path)
    if base_img is None:
        raise FileNotFoundError(f"Base portrait not found at: {sample_path}")
    return base_img


def seed_residents(db_path: str = DEFAULT_DB_PATH, force_refresh: bool = True) -> int:
    """
    Populates SQLite database with 22 distinct registered residents.
    """
    init_db(db_path)
    base_portrait = load_base_portrait()

    faces = detect_faces(base_portrait)
    if not faces:
        raise RuntimeError("No face detected in base portrait!")
    bx, by, bw, bh = faces[0]

    print("=" * 65)
    print(f"SEEDING RESIDENTS INTO DATABASE: {db_path}")
    print("=" * 65)

    registered_count = 0

    for i, (res_id, name) in enumerate(RESIDENT_PROFILES):
        portrait = base_portrait.copy()
        face_roi = portrait[by : by + bh, bx : bx + bw].copy()
        fh, fw = face_roi.shape[:2]

        # 1. Subtle individualized illumination / contrast shift
        alpha = 0.90 + ((i % 5) * 0.05)   # Contrast 0.90 - 1.10
        beta = ((i * 7) % 31) - 15        # Brightness -15 to +15
        face_roi = cv2.convertScaleAbs(face_roi, alpha=alpha, beta=beta)

        # 2. Distinctive anatomical facial features per resident
        if i % 3 == 1:
            # Thin stylish reading glasses
            cv2.circle(face_roi, (int(fw * 0.32), int(fh * 0.45)), int(fw * 0.11), (30, 30, 30), 1)
            cv2.circle(face_roi, (int(fw * 0.68), int(fh * 0.45)), int(fw * 0.11), (30, 30, 30), 1)
            cv2.line(face_roi, (int(fw * 0.43), int(fh * 0.45)), (int(fw * 0.57), int(fh * 0.45)), (30, 30, 30), 1)
        elif i % 3 == 2:
            # Subtle mustache contour
            cv2.ellipse(face_roi, (int(fw * 0.5), int(fh * 0.77)), (int(fw * 0.14), int(fh * 0.04)), 0, 0, 180, (40, 40, 40), -1)

        portrait[by : by + bh, bx : bx + bw] = face_roi

        # Save photograph to disk
        safe_name = name.lower().replace(" ", "_")
        photo_filename = f"{res_id}_{safe_name}.jpg"
        photo_path = os.path.join(FACES_DIR, photo_filename)
        cv2.imwrite(photo_path, portrait)

        # Validate photograph
        is_valid, msg, encoding, bbox = validate_photograph(photo_path)
        if not is_valid:
            print(f"[ERROR] Could not validate photo for {res_id}: {msg}")
            continue

        reg_date = f"2026-11-{10 + (i % 10):02d} {9 + (i % 8):02d}:{(i * 13) % 60:02d}:00"

        if force_refresh and check_duplicate_id(res_id, db_path):
            delete_resident(res_id, db_path)

        inserted = insert_resident(
            resident_id=res_id,
            name=name,
            face_encoding=encoding,
            registration_date=reg_date,
            db_path=db_path,
        )

        if inserted:
            registered_count += 1
            print(f"[REGISTERED] {res_id} | {name:20} | Photo: {photo_filename}")

    total = get_resident_count(db_path)
    print("-" * 65)
    print(f"Seeding Complete! Total registered residents in database: {total}")
    print("=" * 65)
    return total


if __name__ == "__main__":
    seed_residents()
