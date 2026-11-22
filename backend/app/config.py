"""
backend/app/config.py
Configuration and project path anchors.
"""

import os
from pathlib import Path

# Project root is the parent of backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

DATABASE_DIR = PROJECT_ROOT / "database"
DB_PATH = DATABASE_DIR / "society_security.db"

DATASET_DIR = PROJECT_ROOT / "dataset"
RESIDENTS_DIR = DATASET_DIR / "residents"
UNKNOWN_DIR = DATASET_DIR / "unknown"

EVALUATION_DIR = PROJECT_ROOT / "evaluation_results"
EVAL_SUMMARY_PATH = EVALUATION_DIR / "evaluation_summary.txt"
EVAL_CSV_PATH = EVALUATION_DIR / "test_results.csv"

# CORS origins for React Vite dev server
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
