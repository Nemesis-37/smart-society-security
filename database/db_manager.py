"""
Database Management Module for Smart Society Security System.
Handles SQLite connection, schema creation, and resident CRUD operations.
"""

import os
import sqlite3
import datetime
import numpy as np
from typing import List, Dict, Optional, Tuple, Any

# Default path for the database file inside a 'data' folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "society_security.db")


def serialize_encoding(encoding: np.ndarray) -> bytes:
    """
    Serializes a numpy face encoding array into raw bytes for SQLite BLOB storage.
    Ensures high performance and lossless reconstruction.
    """
    if encoding is None:
        raise ValueError("Encoding cannot be None")
    
    arr = np.ascontiguousarray(encoding, dtype=np.float32)
    # Store shape and bytes
    return arr.tobytes()


def deserialize_encoding(data: bytes, shape: Tuple[int, ...] = (128,)) -> np.ndarray:
    """
    Deserializes raw BLOB bytes from SQLite back into a float32 numpy array.
    """
    if data is None:
        return None
    return np.frombuffer(data, dtype=np.float32).copy()


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Opens a connection to the SQLite database.
    Ensures the parent directory exists and configures row_factory.
    """
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enables dict-like column access
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes the SQLite database schema if tables do not exist.
    Creates:
      - residents: resident_id, name, face_encoding, registration_date
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS residents (
                resident_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                face_encoding BLOB NOT NULL,
                registration_date TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def check_duplicate_id(resident_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Checks if a resident_id already exists in the database.
    Returns True if duplicate, False otherwise.
    """
    clean_id = str(resident_id).strip()
    if not clean_id:
        return False
    
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM residents WHERE resident_id = ?", (clean_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def insert_resident(
    resident_id: str,
    name: str,
    face_encoding: np.ndarray,
    registration_date: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> bool:
    """
    Inserts a new resident into the database.
    Validates input parameters and rejects duplicates.
    
    Parameters:
        resident_id (str): Unique resident identifier (e.g. 'RES-001')
        name (str): Full resident name
        face_encoding (np.ndarray): 1D float32 numpy array representing the face
        registration_date (str, optional): ISO formatted timestamp. Defaults to now.
        db_path (str): Database file path
        
    Returns:
        bool: True if insertion succeeded, False if validation failed or duplicate exists.
    """
    clean_id = str(resident_id).strip()
    clean_name = str(name).strip()
    
    if not clean_id:
        raise ValueError("Resident ID cannot be empty.")
    if not clean_name:
        raise ValueError("Resident Name cannot be empty.")
    if face_encoding is None or len(face_encoding) == 0:
        raise ValueError("Face encoding must be a non-empty numpy array.")
    
    if check_duplicate_id(clean_id, db_path):
        return False  # Duplicate ID detected
    
    if registration_date is None:
        registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    blob_data = serialize_encoding(face_encoding)
    
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO residents (resident_id, name, face_encoding, registration_date)
            VALUES (?, ?, ?, ?)
            """,
            (clean_id, clean_name, blob_data, registration_date),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_resident_by_id(resident_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieves a resident by their unique resident_id.
    Returns a dictionary with deserialized face_encoding, or None if not found.
    """
    clean_id = str(resident_id).strip()
    conn = get_connection(db_path)
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


def get_all_residents(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves all registered residents from the database.
    Returns a list of dictionaries with deserialized face encodings.
    """
    conn = get_connection(db_path)
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


def get_resident_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Returns the total count of registered residents in the database.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM residents")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def delete_resident(resident_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Deletes a resident by their resident_id.
    Returns True if a record was deleted, False otherwise.
    """
    clean_id = str(resident_id).strip()
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM residents WHERE resident_id = ?", (clean_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
