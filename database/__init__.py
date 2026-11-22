"""Database package for Smart Society Security System."""
from .db_manager import (
    init_db,
    insert_resident,
    get_all_residents,
    get_resident_by_id,
    check_duplicate_id,
    delete_resident,
    get_resident_count,
    serialize_encoding,
    deserialize_encoding,
    DEFAULT_DB_PATH,
)

__all__ = [
    "init_db",
    "insert_resident",
    "get_all_residents",
    "get_resident_by_id",
    "check_duplicate_id",
    "delete_resident",
    "get_resident_count",
    "serialize_encoding",
    "deserialize_encoding",
    "DEFAULT_DB_PATH",
]
