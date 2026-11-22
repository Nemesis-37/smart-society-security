# Smart Society Security System – Project Report

**Course:** Computer Vision  
**Submission Date:** November 2026  
**Technology:** Python 3.13 · OpenCV · SQLite · Matplotlib  

---

## 1. Introduction

The Smart Society Security System is a real-time face-recognition access-control system developed as a college Computer Vision project. It addresses the problem of manual visitor verification in gated residential communities by automating entry decisions using laptop webcam video and stored resident face encodings.

The system grants **ENTRY ALLOWED** (displayed in green) to registered residents and **ENTRY REJECTED** (displayed in red) to unrecognised persons, with the resident name displayed when recognised.

---

## 2. Problem Statement

Traditional security in gated societies relies on manual log books, printed ID cards, and security guard judgment. This approach is error-prone, slow, and unscalable. A computer-vision-based face-recognition system can automate identity verification in real time.

**Goal:** Build a lightweight, Python-based face recognition security gate that:
- Runs on commodity hardware (a laptop with built-in webcam).
- Requires no specialised deep learning accelerators.
- Stores resident data securely in a local database.
- Provides real-time decisions with sub-second latency.

---

## 3. System Architecture

```
Input (Webcam / Image)
        │
        ▼
Haar Cascade Face Detection (OpenCV)
        │
        ▼
Face ROI Extraction (8% margin crop)
        │
        ▼
Preprocessing: Grayscale → Resize 100×100 → CLAHE
        │
        ▼
Sobel Gradient Computation (Gx, Gy → Magnitude, Angle)
        │
        ▼
Spatial Grid HOG (4×4 cells × 8 bins = 128-D vector)
        │
        ▼
L2 Normalization (local block + global)
        │
        ▼
Euclidean Distance Comparison (vs. SQLite database)
        │
        ├── distance ≤ 0.50 → ENTRY ALLOWED
        └── distance >  0.50 → ENTRY REJECTED
```

---

## 4. Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| Programming Language | Python 3.13 | Modern, widely supported |
| Face Detection | OpenCV Haar Cascade | Pre-trained, fast, no GPU needed |
| Face Encoding | Custom HOG (Sobel + 4×4 grid + 8 bins) | Python 3.13 compatible; no dlib required |
| Database | SQLite 3 | Embedded, zero-configuration, standard library |
| Image Processing | NumPy, OpenCV | Efficient array operations |
| Evaluation | Scikit-learn, Matplotlib | Standard ML evaluation pipeline |

---

## 5. Face Encoding Algorithm

### Why not use `dlib` / `face_recognition`?
The popular `dlib` library provides a 128-D ResNet-based face descriptor with high accuracy. However, its prebuilt Python wheels are not available for Python 3.13 on Windows (as of November 2026). Building from source requires CMake, Visual C++ Build Tools, and a compatible Boost version — infeasible in a constrained lab environment.

### Custom 128-D HOG Encoding

**Step 1 – Canonical Resizing:**  
Face ROI is resized to 100 × 100 pixels using bilinear interpolation.

**Step 2 – CLAHE Normalisation:**  
Contrast Limited Adaptive Histogram Equalisation (clipLimit=2.0, tileGridSize=8×8) normalises illumination across the face.

**Step 3 – Sobel Gradient:**
$$G_x = \text{Sobel}(I, x),\quad G_y = \text{Sobel}(I, y)$$
$$\text{Magnitude} = \sqrt{G_x^2 + G_y^2},\quad \theta = \arctan\!\left(\frac{G_y}{G_x}\right)$$

**Step 4 – Spatial Gradient Histogram:**  
The 100 × 100 image is divided into a 4 × 4 grid of 25 × 25-pixel cells. For each cell, edge magnitudes are accumulated into 8 orientation bins (45° each), yielding a 128-dimensional feature vector.

**Step 5 – Normalisation:**  
Each 8-D cell histogram is locally L2-normalised, then the full 128-D vector is globally L2-normalised to lie on the unit hypersphere. This makes the encoding robust to overall brightness scale.

---

## 6. Face Detection

Haar Cascade classifiers (`haarcascade_frontalface_default.xml`, shipped with OpenCV) are used for face localisation. Parameters:

| Parameter | Value | Effect |
|-----------|-------|--------|
| scaleFactor | 1.1 | Multi-scale detection step |
| minNeighbors | 5 | False-positive suppression |
| minSize | (40, 40) | Minimum detectable face |

---

## 7. Database Design

SQLite database: `database/society_security.db`

**Table: `residents`**

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| resident_id | TEXT | PRIMARY KEY | Unique ID (R001–R022) |
| name | TEXT | NOT NULL | Full resident name |
| face_encoding | BLOB | NOT NULL | 128 × float32 = 512 bytes |
| registration_date | TEXT | NOT NULL | ISO 8601 timestamp |

Face encodings are serialised via `numpy.ndarray.tobytes()` and deserialised with `numpy.frombuffer()`, ensuring lossless round-trip storage.

---

## 8. Recognition Logic

For each detected webcam face:
1. Generate 128-D encoding from live ROI.
2. Compute Euclidean distance to every stored resident encoding.
3. Find the minimum distance `d_min`.
4. If `d_min ≤ threshold (0.50)`: ENTRY ALLOWED → display resident name.
5. Else: ENTRY REJECTED → display "Unknown Person".

**Threshold Justification:**  
Euclidean distance between the same person's same photo = ~0.06 (rounding from normalisation noise). Distance to a random encoding = ~0.67. A threshold of 0.50 provides a clear separation in controlled conditions.

---

## 9. Resident Registration

Registration supports two modes:
1. **Webcam capture** – live frame is captured, validated (single face required), encoded and stored.
2. **File upload** – existing JPEG/PNG is validated and encoded.

Validation rules:
- Exactly one face must be detected (multi-face and no-face photos are rejected).
- Duplicate resident IDs are rejected.
- Minimum image resolution: 50 × 50 px.

---

## 10. Phase Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Environment setup | ✅ Complete |
| 2 | SQLite database layer | ✅ Complete |
| 3 | Resident registration | ✅ Complete |
| 4 | Live webcam face detection | ✅ Complete |
| 5 | Face recognition engine | ✅ Complete |
| 6 | Security gate interface | ✅ Complete |
| 7 | Performance evaluation | ✅ Complete |
| 8 | Final review & documentation | ✅ Complete |

---

## 11. Evaluation Results

### Test Dataset Construction

| Category | Count | Method |
|----------|-------|--------|
| Genuine – Standard (2° warp) | 22 | Photo augmentation |
| Genuine – Low Light (alpha 0.75, beta -20) | 22 | Photo augmentation |
| Genuine – Angled (8° rotation) | 22 | Photo augmentation |
| Genuine – Blurred (Gaussian 5×5) | 22 | Photo augmentation |
| Intruder – Synthetic random encodings | 88 | Random L2-normalised 128-D vectors |
| **Total** | **176** | |

### Performance Metrics (Threshold = 0.50)

| Metric | Value |
|--------|-------|
| True Positive (TP) | 88 |
| True Negative (TN) | 88 |
| False Positive (FP) | 0 |
| False Negative (FN) | 0 |
| Accuracy | 100.00% |
| Precision | 100.00% |
| Recall | 100.00% |
| F1-Score | 100.00% |

### Confusion Matrix

```
                  Predicted
                  Rejected  Allowed
True  Unregistered    88       0
      Registered       0      88
```

### Analysis of Perfect Scores

The 100% metrics are explained by:
1. **Augmentation-based genuine samples** – the same photo base is used for both registration and testing (with mild augmentations). The HOG encoding is invariant to these small changes.
2. **Synthetic intruders** – random L2-normalised vectors produce distances of ~0.67 (well above the 0.50 threshold), making them trivially rejectable.

**Real-world expectation:**  
In a live deployment with real intruders (actual photographs of non-residents), performance would decrease, particularly for:
- Large face angle differences (> 30°).
- Very low lighting (< 50 lux).
- Motion blur from fast movement.

---

## 12. Environmental Robustness

| Condition | Accuracy |
|-----------|----------|
| Standard (2° warp) | 100% |
| Low Light | 100% |
| Angled (8°) | 100% |
| Blurred (5×5 Gaussian) | 100% |
| Synthetic Intruder | 100% |

Small augmentations (< 8° rotation, mild blur, modest brightness reduction) do not affect the gradient-based HOG encoding significantly, because CLAHE pre-normalises illumination and the spatial gradient histograms are inherently orientation-binned.

---

## 13. Limitations and Future Work

**Limitations:**
1. Only frontal faces detected (single Haar cascade).
2. HOG encoding less discriminative than deep-learning descriptors for real-world intruders.
3. No liveness detection (a photo can spoof the system).
4. Synthetic intruders do not reflect real-world attack difficulty.
5. Single sample per resident (no multi-angle registration).

**Future Enhancements:**
- Integrate `InsightFace` or ONNX-exported FaceNet for stronger embeddings.
- Multi-angle registration (at least 3 poses per resident).
- Liveness detection (blink or depth cues).
- Alert logging to file/email on ENTRY REJECTED events.
- Web dashboard for remote monitoring.

---

## 14. Conclusion

The Smart Society Security System demonstrates a complete end-to-end Computer Vision pipeline — from raw webcam frames through face detection, encoding, database storage and real-time gate decisions. It is implemented entirely in Python using standard, open-source libraries and operates on commodity hardware without any GPU or cloud dependency.

The system correctly enforces access control decisions in controlled conditions and provides a solid foundation for further improvement toward production deployment.

---

*Report generated: November 2026*  
*Python 3.13.7 · OpenCV 5.1.0 · SQLite 3 · NumPy 2.4.4 · scikit-learn 1.9.1*
