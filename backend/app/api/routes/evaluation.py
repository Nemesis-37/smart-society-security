"""
backend/app/api/routes/evaluation.py
Evaluation Reports and Visualization Endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import re
from backend.app.config import EVALUATION_DIR, EVAL_SUMMARY_PATH
from backend.app.schemas import EvaluationSummary

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/summary", response_model=EvaluationSummary)
def get_evaluation_summary():
    """
    Returns authentic metrics parsed from evaluation_results/evaluation_summary.txt.
    """
    if not os.path.exists(EVAL_SUMMARY_PATH):
        raise HTTPException(
            status_code=404,
            detail="Evaluation summary has not been generated yet. Run Phase 7 evaluation.",
        )

    with open(EVAL_SUMMARY_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    def _extract_int(pattern, default=0):
        m = re.search(pattern, content)
        return int(m.group(1)) if m else default

    def _extract_float(pattern, default=0.0):
        m = re.search(pattern, content)
        return float(m.group(1)) if m else default

    date_match = re.search(r"Generated:\s*([^\n\r]+)", content)

    return EvaluationSummary(
        total_samples=_extract_int(r"Total test samples\s*:\s*(\d+)"),
        genuine_count=_extract_int(r"Genuine \(registered\)\s*:\s*(\d+)"),
        intruder_count=_extract_int(r"Intruder \(synthetic\)\s*:\s*(\d+)"),
        threshold=_extract_float(r"Threshold used\s*:\s*([\d\.]+)"),
        tp=_extract_int(r"True\s*Positive \(TP\)\s*:\s*(\d+)"),
        tn=_extract_int(r"True\s*Negative \(TN\)\s*:\s*(\d+)"),
        fp=_extract_int(r"False\s*Positive \(FP\)\s*:\s*(\d+)"),
        fn=_extract_int(r"False\s*Negative \(FN\)\s*:\s*(\d+)"),
        accuracy=_extract_float(r"Accuracy\s*:\s*([\d\.]+)"),
        precision=_extract_float(r"Precision\s*:\s*([\d\.]+)"),
        recall=_extract_float(r"Recall\s*:\s*([\d\.]+)"),
        f1_score=_extract_float(r"F1-Score\s*:\s*([\d\.]+)"),
        timestamp=date_match.group(1).strip() if date_match else "Unknown",
    )


@router.get("/plot/{filename}")
def get_evaluation_plot(filename: str):
    """
    Serves evaluation charts: confusion_matrix.png, environmental_robustness.png, threshold_analysis.png.
    """
    allowed_plots = {
        "confusion_matrix": "confusion_matrix.png",
        "environmental_robustness": "environmental_robustness.png",
        "threshold_analysis": "threshold_analysis.png",
    }
    clean_name = filename.replace(".png", "")
    if clean_name not in allowed_plots:
        raise HTTPException(status_code=404, detail="Invalid plot name requested.")

    path = os.path.join(EVALUATION_DIR, allowed_plots[clean_name])
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Plot {filename} not found.")

    return FileResponse(path, media_type="image/png")
