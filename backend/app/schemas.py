"""
backend/app/schemas.py
Pydantic Request & Response Models.
Ensures zero internal face encoding BLOB leakage to public responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HealthResponse(BaseModel):
    status: str = "healthy"
    database_connected: bool
    resident_count: int
    timestamp: str


class ResidentResponse(BaseModel):
    resident_id: str
    name: str
    registration_date: str
    photo_url: str


class ResidentRegisterResponse(BaseModel):
    success: bool
    message: str
    resident_id: Optional[str] = None
    name: Optional[str] = None


class DashboardStats(BaseModel):
    total_residents: int
    backend_status: str
    database_status: str
    evaluation_accuracy: Optional[float] = None
    evaluation_f1: Optional[float] = None
    threshold: float
    system_time: str
    genuine_entries: int = 0
    rejected_entries: int = 0


class GateStatus(BaseModel):
    status: str
    threshold: float
    resident_count: int
    camera_available: bool


class ThresholdUpdate(BaseModel):
    threshold: float = Field(..., ge=0.05, le=1.0)


class EvaluationSummary(BaseModel):
    total_samples: int
    genuine_count: int
    intruder_count: int
    threshold: float
    tp: int
    tn: int
    fp: int
    fn: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    timestamp: str


class AccessLogItem(BaseModel):
    id: int
    timestamp: str
    resident_id: Optional[str]
    name: str
    decision: str
    distance: float
    confidence: float
