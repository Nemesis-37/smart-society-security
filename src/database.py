"""
src/database.py
SQLite Database Connectivity and Resident Management Module.
Implements secure, parameterized CRUD operations and binary BLOB storage for face encodings.
"""

import os
import sqlite3
import datetime
from typing import List, Dict, Optional, Any, Tuple
import numpy as np

# Default SQLite database path in database/ folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
DEFAULT_DB_PATH = os.path.join(DATABASE_DIR, "society_security.db")


def serialize_encoding(encoding: np.ndarray) -> bytes:
    """
    Serializes a numpy face encoding array into raw bytes for SQLite BLOB storage.
    Ensures exact, lossless float32 vector reconstruction.
    """
    if encoding is None:
        raise ValueError("Face encoding cannot be None.")
    arr = np.ascontiguousarray(encoding, dtype=np.float32)
    return arr.tobytes()


def deserialize_encoding(data: bytes) -> np.ndarray:
    """
    Deserializes raw BLOB bytes from SQLite back into a float32 numpy array.
    """
    if data is None:
        return None
    return np.frombuffer(data, dtype=np.float32).copy()


def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Ensures the parent directory exists and enables Row factory.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path: str = None) -> None:
    """
    Initializes the SQLite database schema if it does not already exist.
    Creates table 'residents' with:
      - resident_id (Primary Key)
      - name (Text, Not Null)
      - face_encoding (BLOB, Not Null)
      - registration_date (Text, Not Null)
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS residents (
                    resident_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    face_encoding BLOB NOT NULL,
                    registration_date TEXT NOT NULL
                )
                """
            )
    finally:
        conn.close()


def check_duplicate_resident(resident_id: str, db_path: str = None) -> bool:
    """
    Checks if a resident_id already exists in the database.
    Uses parameterized SQL queries. Returns True if duplicate, False otherwise.
    """
    clean_id = str(resident_id).strip().upper()
    if not clean_id:
        return False

    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM residents WHERE resident_id = ?", (clean_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def add_resident(
    resident_id: str,
    name: str,
    face_encoding: np.ndarray,
    registration_date: Optional[str] = None,
    db_path: str = None,
) -> bool:
    """
    Inserts a new resident record into the SQLite database.
    
    Parameters:
        resident_id (str): Unique ID (e.g. 'R001')
        name (str): Full name of the resident
        face_encoding (np.ndarray): 1D float32 array
        registration_date (str, optional): ISO datetime string
        db_path (str, optional): Custom DB path
        
    Returns:
        bool: True on success, False if duplicate or invalid.
    """
    clean_id = str(resident_id).strip().upper()
    clean_name = str(name).strip()

    if not clean_id:
        raise ValueError("Validation Error: Resident ID cannot be empty.")
    if not clean_name:
        raise ValueError("Validation Error: Resident Name cannot be empty.")
    if face_encoding is None or len(face_encoding) == 0:
        raise ValueError("Validation Error: Face encoding cannot be empty.")

    # Ensure database table exists
    initialize_database(db_path)

    # Check duplicate
    if check_duplicate_resident(clean_id, db_path):
        return False

    if registration_date is None:
        registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    blob_data = serialize_encoding(face_encoding)

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO residents (resident_id, name, face_encoding, registration_date)
                VALUES (?, ?, ?, ?)
                """,
                (clean_id, clean_name, blob_data, registration_date),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_resident_by_id(resident_id: str, db_path: str = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves a resident record by resident_id.
    Returns a dictionary with deserialized face_encoding, or None if not found.
    """
    clean_id = str(resident_id).strip().upper()
    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT resident_id, name, face_encoding, registration_date FROM residents WHERE resident_id = ?",
            (clean_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "resident_id": row["resident_id"],
            "name": row["name"],
            "face_encoding": deserialize_encoding(row["face_encoding"]),
            "registration_date": row["registration_date"],
        }
    finally:
        conn.close()


def get_all_residents(db_path: str = None) -> List[Dict[str, Any]]:
    """
    Retrieves all registered residents from the database.
    Returns list of dicts with reconstituted face encodings.
    """
    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT resident_id, name, face_encoding, registration_date FROM residents ORDER BY resident_id ASC"
        )
        rows = cursor.fetchall()
        residents = []
        for row in rows:
            residents.append(
                {
                    "resident_id": row["resident_id"],
                    "name": row["name"],
                    "face_encoding": deserialize_encoding(row["face_encoding"]),
                    "registration_date": row["registration_date"],
                }
            )
        return residents
    finally:
        conn.close()


def delete_resident(resident_id: str, db_path: str = None) -> bool:
    """
    Deletes a resident record by resident_id.
    Returns True if record was deleted, False otherwise.
    """
    clean_id = str(resident_id).strip().upper()
    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM residents WHERE resident_id = ?", (clean_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()
