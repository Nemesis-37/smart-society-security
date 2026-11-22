"""Models package for face detection, encoding, and recognition."""
from .face_pipeline import (
    detect_faces,
    generate_face_encoding,
    calculate_face_distance,
    validate_photograph,
    CASCADE_PATH,
)
from .recognizer import SecurityRecognizer, DEFAULT_THRESHOLD

__all__ = [
    "detect_faces",
    "generate_face_encoding",
    "calculate_face_distance",
    "validate_photograph",
    "CASCADE_PATH",
    "SecurityRecognizer",
    "DEFAULT_THRESHOLD",
]
