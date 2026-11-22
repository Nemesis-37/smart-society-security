"""
backend/app/api/routes/health.py
Health Check Endpoint.
"""

from fastapi import APIRouter
import datetime
from backend.app.schemas import HealthResponse
from src.database import get_all_residents, DEFAULT_DB_PATH

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health():
    """
    Checks backend health and actual SQLite database connectivity.
    """
    try:
        residents = get_all_residents(str(DEFAULT_DB_PATH))
        connected = True
        count = len(residents)
    except Exception:
        connected = False
        count = 0

    return HealthResponse(
        status="healthy" if connected else "degraded",
        database_connected=connected,
        resident_count=count,
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
