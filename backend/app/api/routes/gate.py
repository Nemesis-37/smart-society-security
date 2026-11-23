"""
backend/app/api/routes/gate.py
Gate controls, live MJPEG streaming, status telemetry, threshold adjustment and DB reload.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from backend.app.schemas import ThresholdUpdate
from backend.app.camera_manager import camera_manager

router = APIRouter(prefix="/gate", tags=["Gate"])


@router.post("/start")
def start_camera():
    """
    Starts the live camera capture and face recognition loop.
    Guarantees a single active session (idempotent).
    """
    success = camera_manager.start(camera_index=0)
    if not success and not camera_manager.is_running:
        return {
            "success": False,
            "camera_active": False,
            "message": "Camera hardware could not be initialized. Check device permissions or run in native desktop terminal.",
        }
    return {
        "success": True,
        "camera_active": True,
        "message": "Live camera capture session started successfully.",
    }


@router.post("/stop")
def stop_camera():
    """
    Stops the camera capture loop and releases the webcam hardware.
    """
    camera_manager.stop()
    return {
        "success": True,
        "camera_active": False,
        "message": "Live camera capture stopped and hardware released.",
    }


@router.get("/status")
def get_gate_status():
    """
    Returns live telemetry: camera state, FPS, gate status, threshold, and entrant details.
    """
    return camera_manager.get_status()


@router.get("/stream")
def get_mjpeg_stream():
    """
    Provides a real-time MJPEG live video stream compatible with standard <img> tags.
    """
    return StreamingResponse(
        camera_manager.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/threshold")
def update_threshold(body: ThresholdUpdate):
    """
    Updates the Euclidean distance recognition threshold in real time.
    """
    camera_manager.recognizer.threshold = round(body.threshold, 2)
    return {
        "success": True,
        "threshold": camera_manager.recognizer.threshold,
        "message": f"Recognition threshold updated to {camera_manager.recognizer.threshold:.2f}",
    }


@router.post("/reload")
def reload_database():
    """
    Hot-reloads resident encodings from SQLite into memory without restarting.
    """
    count = camera_manager.recognizer.reload_residents()
    return {
        "success": True,
        "resident_count": count,
        "message": f"Successfully reloaded {count} resident(s) from database.",
    }
