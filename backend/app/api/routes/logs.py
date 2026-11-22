"""
backend/app/api/routes/logs.py
Access Logs Endpoint.
Returns authentic access logs (empty list when none recorded yet).
"""

from fastapi import APIRouter
from typing import List
from backend.app.schemas import AccessLogItem

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=List[AccessLogItem])
def get_access_logs():
    """
    Returns authentic gate entry event logs.
    Currently returns an empty list as entry events are recorded during live gate operation (Phase 5).
    Does NOT invent fake entry records.
    """
    return []
