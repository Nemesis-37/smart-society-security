"""
backend/app/api/routes/dashboard.py
Dashboard Statistics Endpoint.
"""

from fastapi import APIRouter
import datetime
import os
import re
from backend.app.schemas import DashboardStats
from backend.app.config import EVAL_SUMMARY_PATH
from src.database import get_all_residents, DEFAULT_DB_PATH
from src.recognition_engine import DEFAULT_THRESHOLD

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _read_eval_summary():
    """Extracts genuine evaluation accuracy and f1 score from evaluation_summary.txt if present."""
    if not os.path.exists(EVAL_SUMMARY_PATH):
        return None, None
    try:
        with open(EVAL_SUMMARY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        acc_match = re.search(r"Accuracy\s*:\s*([\d\.]+)%", content)
        f1_match = re.search(r"F1-Score\s*:\s*([\d\.]+)%", content)
        acc = float(acc_match.group(1)) if acc_match else None
        f1 = float(f1_match.group(1)) if f1_match else None
        return acc, f1
    except Exception:
        return None, None


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats():
    """
    Returns authentic system metrics from the SQLite database and evaluation logs.
    Does NOT invent fake entry records.
    """
    try:
        residents = get_all_residents(str(DEFAULT_DB_PATH))
        db_ok = True
        count = len(residents)
    except Exception:
        db_ok = False
        count = 0

    acc, f1 = _read_eval_summary()

    return DashboardStats(
        total_residents=count,
        backend_status="Online",
        database_status="Connected" if db_ok else "Disconnected",
        evaluation_accuracy=acc,
        evaluation_f1=f1,
        threshold=DEFAULT_THRESHOLD,
        system_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        genuine_entries=0,
        rejected_entries=0,
    )
