"""
backend/app/api/routes/logs.py
Gate Entry and Access Logs API.
Retrieves real entry event records from SQLite entry_logs table with search,
status filtering, and pagination support.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict, Any
import sqlite3
from backend.app.config import DB_PATH
from backend.app.schemas import AccessLogItem

router = APIRouter(prefix="/logs", tags=["Logs"])


def _get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@router.get("", response_model=Dict[str, Any])
def get_access_logs(
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by 'ENTRY ALLOWED' or 'ENTRY REJECTED'"),
    limit: int = 50,
    offset: int = 0,
):
    """
    Returns authentic gate entry event logs with search, filtering, and pagination.
    Does NOT invent fake records.
    """
    conn = _get_connection()
    try:
        # Build query dynamically with parameterization
        where_clauses = []
        params = []

        if search and isinstance(search, str) and search.strip():
            clean_search = f"%{search.strip()}%"
            where_clauses.append("(person_name LIKE ? OR resident_id LIKE ?)")
            params.extend([clean_search, clean_search])

        if status_filter and isinstance(status_filter, str) and status_filter.strip():
            where_clauses.append("status = ?")
            params.append(status_filter.strip())

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Total count query
        count_cursor = conn.cursor()
        count_cursor.execute(f"SELECT COUNT(*) FROM entry_logs {where_sql}", params)
        total_count = count_cursor.fetchone()[0]

        # Paginated fetch
        data_cursor = conn.cursor()
        fetch_params = params + [limit, offset]
        data_cursor.execute(
            f"""
            SELECT id, resident_id, person_name, status, timestamp, face_distance
            FROM entry_logs
            {where_sql}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            fetch_params,
        )
        rows = data_cursor.fetchall()

        logs = []
        for r in rows:
            dist = r["face_distance"]
            # Estimate confidence from distance if available
            conf = max(0.0, min(1.0, 1.0 - (dist / 0.50))) if dist is not None else 0.0
            logs.append(
                {
                    "id": r["id"],
                    "resident_id": r["resident_id"],
                    "name": r["person_name"],
                    "decision": r["status"],
                    "timestamp": r["timestamp"],
                    "distance": round(dist, 4) if dist is not None else 0.0,
                    "confidence": round(conf, 4),
                }
            )

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "items": logs,
        }
    finally:
        conn.close()


@router.get("/{log_id}", response_model=Dict[str, Any])
def get_log_by_id(log_id: int):
    """
    Retrieves a single entry log record by ID.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, resident_id, person_name, status, timestamp, face_distance FROM entry_logs WHERE id = ?",
            (log_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entry log record #{log_id} not found.",
            )
        dist = row["face_distance"]
        conf = max(0.0, min(1.0, 1.0 - (dist / 0.50))) if dist is not None else 0.0
        return {
            "id": row["id"],
            "resident_id": row["resident_id"],
            "name": row["person_name"],
            "decision": row["status"],
            "timestamp": row["timestamp"],
            "distance": round(dist, 4) if dist is not None else 0.0,
            "confidence": round(conf, 4),
        }
    finally:
        conn.close()
