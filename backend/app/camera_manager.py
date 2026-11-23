"""
backend/app/camera_manager.py
Thread-safe Singleton Camera Manager for FastAPI.
Integrates cv2.VideoCapture with src.recognition_engine.SecurityRecognizer
and src.security_gate.annotate_frame for real-time MJPEG video streaming.
Implements event-based entry logging with cooldown to avoid duplicate flooding.
"""

import time
import threading
import datetime
import sqlite3
import os
import cv2
import numpy as np
from typing import Optional, Dict, Any, Generator

from backend.app.config import DB_PATH
from src.recognition_engine import (
    SecurityRecognizer,
    DEFAULT_THRESHOLD,
    GATE_ALLOWED,
    GATE_REJECTED,
    GATE_NO_FACE,
)
from src.security_gate import annotate_frame, _draw_top_hud
from src.webcam_detection import initialize_camera


class CameraManager:
    """
    Singleton Camera Manager ensuring only one camera capture session is active at a time.
    Provides thread-safe access to frames, real-time recognition metadata,
    and throttled entry event logging.
    """
    _instance: Optional["CameraManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running: bool = False
        self.camera_index: int = 0
        self.thread: Optional[threading.Thread] = None
        self.frame_lock = threading.Lock()
        
        self.current_frame: Optional[np.ndarray] = None
        self.current_annotated_frame: Optional[np.ndarray] = None
        
        # Recognition engine instance
        self.recognizer = SecurityRecognizer(
            db_path=str(DB_PATH),
            threshold=DEFAULT_THRESHOLD
        )
        
        # Telemetry state
        self.gate_status: str = GATE_NO_FACE
        self.last_results: list = []
        self.fps: float = 0.0
        self.last_decision: Dict[str, Any] = {
            "decision": GATE_NO_FACE,
            "resident_id": None,
            "name": "No face detected",
            "distance": None,
            "confidence": 0.0,
            "timestamp": None,
        }
        
        # Cooldown management for entry logging (prevents 30fps log flood)
        self.last_logged_time: Dict[str, float] = {}  # key -> last log timestamp
        self.LOG_COOLDOWN_SECONDS: float = 5.0
        
        # Initialize entry_logs database table
        self._ensure_entry_logs_table()

    def _ensure_entry_logs_table(self):
        """Ensures the entry_logs table exists in society_security.db."""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS entry_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        resident_id TEXT,
                        person_name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        face_distance REAL
                    )
                    """
                )
            conn.close()
        except Exception as e:
            print(f"[CameraManager] Error creating entry_logs table: {e}")

    def log_entry_event(self, resident_id: Optional[str], person_name: str, status: str, distance: Optional[float]):
        """
        Inserts an authentic entry event into SQLite with cooldown throttling.
        """
        now = time.time()
        cooldown_key = f"{resident_id or 'UNKNOWN'}_{status}"
        
        last_time = self.last_logged_time.get(cooldown_key, 0.0)
        if now - last_time < self.LOG_COOLDOWN_SECONDS:
            return  # Throttle continuous recognition of same person/state
            
        self.last_logged_time[cooldown_key] = now
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            conn = sqlite3.connect(str(DB_PATH))
            with conn:
                conn.execute(
                    """
                    INSERT INTO entry_logs (resident_id, person_name, status, timestamp, face_distance)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        resident_id,
                        person_name,
                        status,
                        timestamp_str,
                        round(float(distance), 4) if distance is not None else None
                    )
                )
            conn.close()
            print(f"[Audit Log] Recorded event: {status} - {person_name} ({resident_id or 'Unknown'}) at {timestamp_str}")
        except Exception as e:
            print(f"[CameraManager] Log write error: {e}")

    def start(self, camera_index: int = 0) -> bool:
        """
        Starts the background camera acquisition loop.
        Guarantees only one active camera session.
        """
        with self.frame_lock:
            if self.is_running:
                return True  # Already running

            self.camera_index = camera_index
            self.cap = initialize_camera(index=camera_index)
            
            if self.cap is None or not self.cap.isOpened():
                self.is_running = False
                print("[CameraManager] Could not open camera hardware.")
                return False

            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            print("[CameraManager] Live camera capture session started.")
            return True

    def stop(self):
        """
        Stops the camera loop and safely releases the hardware resources.
        """
        with self.frame_lock:
            self.is_running = False
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            self.thread = None

        self.gate_status = GATE_NO_FACE
        print("[CameraManager] Camera capture session stopped and hardware released.")

    def _capture_loop(self):
        """Continuous background frame acquisition and recognition loop."""
        fps_count = 0
        t0 = time.time()
        fps_current = 0.0

        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.03)
                continue

            # Process frame through OpenCV recognition pipeline
            results, gate_status = self.recognizer.process_frame(frame)
            
            # FPS calculation
            fps_count += 1
            elapsed = time.time() - t0
            if elapsed >= 0.5:
                fps_current = round(fps_count / elapsed, 1)
                fps_count = 0
                t0 = time.time()

            # Annotate HUD & bounding boxes
            annotated = frame.copy()
            annotate_frame(annotated, results, gate_status)
            _draw_top_hud(
                annotated,
                gate_status,
                self.recognizer.resident_count,
                self.recognizer.threshold,
                fps_current
            )

            # Update latest state & log relevant events
            with self.frame_lock:
                self.current_frame = frame
                self.current_annotated_frame = annotated
                self.gate_status = gate_status
                self.last_results = results
                self.fps = fps_current
                
                if results:
                    # Use best / first match
                    best_bbox, best_res = results[0]
                    self.last_decision = {
                        "decision": best_res["decision"],
                        "resident_id": best_res["resident_id"],
                        "name": best_res["name"],
                        "distance": best_res["distance"],
                        "confidence": best_res["confidence"],
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    
                    # Log event
                    if best_res["is_recognized"]:
                        self.log_entry_event(
                            resident_id=best_res["resident_id"],
                            person_name=best_res["name"],
                            status=GATE_ALLOWED,
                            distance=best_res["distance"]
                        )
                    else:
                        self.log_entry_event(
                            resident_id=None,
                            person_name="Unknown Visitor",
                            status=GATE_REJECTED,
                            distance=best_res["distance"]
                        )
                else:
                    self.last_decision = {
                        "decision": GATE_NO_FACE,
                        "resident_id": None,
                        "name": "No face detected",
                        "distance": None,
                        "confidence": 0.0,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

            time.sleep(0.015)  # Cap loop to ~30-40 FPS to conserve CPU

    def get_latest_jpeg(self) -> Optional[bytes]:
        """Encodes the latest annotated frame into JPEG bytes."""
        with self.frame_lock:
            frame = self.current_annotated_frame
            if frame is None:
                # If camera is not active or starting, generate a clean standby graphic
                h, w = 480, 640
                standby = np.full((h, w, 3), 15, dtype=np.uint8)
                msg = "GATE CAMERA STANDBY" if not self.is_running else "INITIALIZING CAMERA..."
                cv2.putText(
                    standby, msg, (w // 2 - 160, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 210, 240), 2, cv2.LINE_AA
                )
                _, buffer = cv2.imencode(".jpg", standby)
                return buffer.tobytes()

            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return buffer.tobytes()

    def generate_mjpeg_stream(self) -> Generator[bytes, None, None]:
        """Generator yielding multipart JPEG frames for FastAPI StreamingResponse."""
        while True:
            jpeg = self.get_latest_jpeg()
            if jpeg:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
                )
            time.sleep(0.035)  # ~28 FPS stream rate

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive telemetry for API responses."""
        with self.frame_lock:
            return {
                "camera_active": self.is_running,
                "gate_status": self.gate_status,
                "fps": self.fps,
                "threshold": self.recognizer.threshold,
                "resident_count": self.recognizer.resident_count,
                "last_decision": self.last_decision,
                "faces_detected": len(self.last_results),
            }


# Singleton accessor
camera_manager = CameraManager()
