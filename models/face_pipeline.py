"""
Face Detection & 128-Dimensional Face Encoding Pipeline.
Pure OpenCV and NumPy implementation designed for high accuracy,
zero dependency issues, and compatibility with Python 3.13 on Windows.
"""

import os
import cv2
import numpy as np
from typing import Tuple, List, Optional, Union

# Load pre-trained OpenCV Haar Cascade for Frontal Face Detection
CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(f"Haar Cascade file not found at: {CASCADE_PATH}")

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


def detect_faces(
    image: np.ndarray,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
    min_size: Tuple[int, int] = (40, 40),
) -> List[Tuple[int, int, int, int]]:
    """
    Detects faces in an image using OpenCV Haar Cascades.
    """
    if image is None or image.size == 0:
        return []

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    gray = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=min_size,
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    return [tuple(map(int, bbox)) for bbox in faces]


def extract_face_roi(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Extracts face Region of Interest (ROI) with standard anatomical margin.
    Guarantees consistent cropping between registration and live recognition.
    """
    x, y, w, h = bbox
    margin = int(0.08 * min(w, h))
    x_start = max(0, x - margin)
    y_start = max(0, y - margin)
    x_end = min(image.shape[1], x + w + margin)
    y_end = min(image.shape[0], y + h + margin)
    return image[y_start:y_end, x_start:x_end]


def generate_face_encoding(face_roi: np.ndarray) -> np.ndarray:
    """
    Generates a 128-dimensional feature encoding vector from a face ROI.
    """
    if face_roi is None or face_roi.size == 0:
        raise ValueError("Invalid face ROI provided.")

    if len(face_roi.shape) == 3:
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = face_roi.copy()

    # Step 1: Canonical Resize
    gray = cv2.resize(gray, (100, 100), interpolation=cv2.INTER_AREA)

    # Step 2: Illumination Normalization via CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    norm = clahe.apply(gray)

    # Step 3: Compute Spatial Gradients (Sobel)
    gx = cv2.Sobel(norm, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(norm, cv2.CV_32F, 0, 1, ksize=3)
    magnitude, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)

    # 8 orientation bins across 360 degrees (45 degrees per bin)
    bin_width = 45.0
    bins = (angle / bin_width).astype(int) % 8

    # Step 4: Extract 16 cells (4x4 grid) x 8 bins = 128 features
    encoding_list = []
    cell_h, cell_w = 25, 25

    for r in range(4):
        for c in range(4):
            cell_mag = magnitude[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]
            cell_bins = bins[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]

            hist = np.zeros(8, dtype=np.float32)
            for b in range(8):
                hist[b] = np.sum(cell_mag[cell_bins == b])

            local_norm = np.linalg.norm(hist) + 1e-6
            hist /= local_norm
            encoding_list.extend(hist)

    vector = np.array(encoding_list, dtype=np.float32)

    # Step 5: Global L2 Unit Vector Normalization
    global_norm = np.linalg.norm(vector)
    if global_norm > 0:
        vector /= global_norm

    return vector


def calculate_face_distance(encoding1: np.ndarray, encoding2: np.ndarray) -> float:
    """
    Calculates Euclidean distance between two 128-dimensional face encodings.
    """
    if encoding1 is None or encoding2 is None:
        raise ValueError("Encodings cannot be None.")
    return float(np.linalg.norm(encoding1 - encoding2))


def validate_photograph(
    image_input: Union[str, np.ndarray],
    strict_single_face: bool = True,
) -> Tuple[bool, str, Optional[np.ndarray], Optional[Tuple[int, int, int, int]]]:
    """
    Validates a photograph for resident registration.
    """
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            return False, f"File does not exist: {image_input}", None, None
        img = cv2.imread(image_input)
        if img is None:
            return False, f"Could not read image file: {image_input}", None, None
    elif isinstance(image_input, np.ndarray):
        img = image_input
    else:
        return False, "Unsupported image input type.", None, None

    if img.size == 0 or img.shape[0] < 50 or img.shape[1] < 50:
        return False, "Image resolution is too low.", None, None

    faces = detect_faces(img)

    if len(faces) == 0:
        return False, "Validation Failed: No face detected in the photograph. Ensure clear lighting.", None, None

    if strict_single_face and len(faces) > 1:
        return (
            False,
            f"Validation Failed: Multiple faces ({len(faces)}) detected. Registration requires exactly one face.",
            None,
            None,
        )

    largest_face = max(faces, key=lambda b: b[2] * b[3])
    face_roi = extract_face_roi(img, largest_face)
    encoding = generate_face_encoding(face_roi)

    return True, "Photograph validated successfully.", encoding, largest_face
