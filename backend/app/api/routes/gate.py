"""
backend/app/api/routes/gate.py
Gate status, threshold tuning and reload endpoints.
"""

from fastapi import APIRouter
from backend.app.schemas import GateStatus, ThresholdUpdate
from src.database import get_all_residents, DEFAULT_DB_PATH
from src.recognition_engine import SecurityRecognizer, DEFAULT_THRESHOLD

router = APIRouter(prefix="/gate", tags=["Gate"])

# Shared recognizer instance for live state management
_recognizer = SecurityRecognizer(db_path=str(DEFAULT_DB_PATH), threshold=DEFAULT_THRESHOLD)


@router.get("/status", response_model=GateStatus)
def get_gate_status():
    """
    Returns current recognition engine configuration and resident count.
    """
    count = _recognizer.resident_count
    return GateStatus(
        status="Active",
        threshold=_recognizer.threshold,
        resident_count=count,
        camera_available=True,
    )


@router.post("/threshold")
def update_threshold(body: ThresholdUpdate):
    """
    Updates the Euclidean distance recognition threshold in real time.
    """
    _recognizer.threshold = round(body.threshold, 2)
    return {
        "success": True,
        "threshold": _recognizer.threshold,
        "message": f"Recognition threshold updated to {_recognizer.threshold:.2f}",
    }


@router.post("/reload")
def reload_database():
    """
    Hot-reloads resident encodings from SQLite into memory.
    """
    count = _recognizer.reload_residents()
    return {
        "success": True,
        "resident_count": count,
        "message": f"Successfully reloaded {count} resident(s) from database.",
    }
