# Viva Questions & Answers – Smart Society Security System

**Subject:** Computer Vision  
**Topics:** OpenCV · Face Detection · Face Encoding · Face Matching · SQLite · Evaluation Metrics

---

## Section A – OpenCV Fundamentals

**Q1. What is OpenCV and why is it used in this project?**  
OpenCV (Open Source Computer Vision Library) is an open-source library for real-time computer vision tasks. In this project it handles webcam capture (`VideoCapture`), Haar Cascade face detection, image preprocessing (CLAHE, Sobel gradients), and display (`imshow`, `rectangle`). It is chosen because it supports Python 3.13 without compilation and provides efficient C++ backends through Python bindings.

**Q2. What is the purpose of `cv2.VideoCapture(0)`?**  
It opens the default webcam (index 0). `cap.read()` returns a Boolean success flag and the captured BGR frame. We always check the flag before processing.

**Q3. What is a BGR image and why does OpenCV use it instead of RGB?**  
OpenCV stores colour images in Blue-Green-Red order (legacy from early camera hardware). Most image processing operations are order-independent (e.g., Sobel), but display functions like `imshow` and saving functions like `imwrite` expect BGR. We convert to grayscale for face processing with `cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)`.

**Q4. What is `cv2.equalizeHist()` and when is it used?**  
It applies global histogram equalisation, spreading pixel intensity values across the full 0–255 range. We apply it on the grayscale image before Haar Cascade detection to improve contrast and make face features more detectable under varying lighting.

**Q5. What is CLAHE and how does it differ from global histogram equalisation?**  
CLAHE (Contrast Limited Adaptive Histogram Equalisation) divides the image into small tiles (8×8 in this project) and equalises each tile independently. A clip limit (2.0) prevents over-amplification of noise. Unlike global equalisation, CLAHE preserves local contrast without washing out evenly lit regions — making it superior for face normalisation before encoding.

---

## Section B – Face Detection

**Q6. How does Haar Cascade face detection work?**  
Haar Cascades use rectangular Haar-like features (differences between adjacent rectangular regions) to detect edges, lines, and patterns associated with faces. A cascade of increasingly selective classifiers (trained by Viola-Jones AdaBoost) rejects non-face windows quickly. Only windows that pass all stages are classified as faces. The detector slides a window at multiple scales to handle different face sizes.

**Q7. What are the key parameters of `detectMultiScale`?**  
- `scaleFactor` (1.1): Image is downscaled by 10% at each pyramid level.
- `minNeighbors` (5): A detection rectangle must have at least 5 overlapping detections to be accepted; reduces false positives.
- `minSize` (40, 40): Faces smaller than 40×40 pixels are ignored.
- `flags` (`CASCADE_SCALE_IMAGE`): Standard multi-scale detection.

**Q8. What is the difference between `scaleFactor=1.1` and `scaleFactor=1.3`?**  
Smaller values (1.1) produce finer detection pyramids, detecting more faces including small ones, but are slower. Larger values (1.3) are faster but may miss small or distant faces. We use 1.1 for thoroughness in real-time conditions.

**Q9. Why do you apply `equalizeHist` before `detectMultiScale`?**  
The Haar Cascade was trained on normalised images. Applying equalisation brings the input closer to the training distribution, improving recall (fewer missed faces) under non-ideal lighting.

**Q10. What is the bounding box returned by `detectMultiScale`?**  
Each element is a tuple `(x, y, w, h)` where `(x, y)` is the top-left corner of the face rectangle, `w` is its width, and `h` its height — all in pixels.

---

## Section C – Face Encoding

**Q11. What is a face encoding?**  
A face encoding is a compact numerical vector that summarises the visual features of a face. Two images of the same person should have similar (close) encodings; images of different people should have dissimilar (distant) encodings.

**Q12. Explain the 128-D encoding pipeline used in this project.**  
1. Resize the face ROI to 100×100 pixels (canonical size).
2. Apply CLAHE for illumination normalisation.
3. Compute Sobel gradients in X and Y directions; convert to magnitude and angle.
4. Divide the image into a 4×4 grid of 25×25-pixel cells.
5. For each cell, accumulate gradient magnitudes into 8 orientation bins (0°–360° in 45° steps).
6. L2-normalise each cell's 8-D histogram; concatenate all 16 cells → 128-D vector.
7. Globally L2-normalise the 128-D vector to unit length.

**Q13. Why is L2 normalisation applied?**  
L2 normalisation maps all encoding vectors onto the unit hypersphere. This makes Euclidean distance equivalent to a cosine similarity measure, removing the effect of overall gradient magnitude (which varies with image brightness) and making comparisons scale-invariant.

**Q14. What are Sobel gradients and why are they used?**  
Sobel operators are 3×3 convolution kernels that compute image derivatives in the X and Y directions:
- `Gx` detects vertical edges.
- `Gy` detects horizontal edges.
- Magnitude `M = √(Gx² + Gy²)` indicates edge strength.
- Angle `θ = arctan(Gy/Gx)` indicates edge direction.
Gradients capture the structural patterns of a face (eye edges, nose bridge, mouth line) that are distinctive per person.

**Q15. Why is the face ROI resized to 100×100 before encoding?**  
Canonical sizing ensures all encoding vectors are computed on the same spatial scale, making distance comparisons meaningful. Without resizing, a small face would produce different histogram statistics than a large face of the same person.

---

## Section D – Face Matching and Recognition

**Q16. How is Euclidean distance calculated between two encodings?**  
$$d = \|\mathbf{e}_1 - \mathbf{e}_2\|_2 = \sqrt{\sum_{i=1}^{128}(e_{1i} - e_{2i})^2}$$
In NumPy: `np.linalg.norm(e1 - e2)`.

**Q17. What threshold is used and how was it chosen?**  
Threshold = **0.50**. The same photo of the same person gives a distance of ~0.06 (near zero, due to normalisation). Random unrelated encodings give distances of ~0.67. A value of 0.50 sits midway between these natural clusters, providing clear separation in controlled conditions.

**Q18. What is ENTRY ALLOWED vs ENTRY REJECTED?**  
- **ENTRY ALLOWED**: The best-matching resident has distance ≤ 0.50 from the detected face encoding. The resident is recognised and their name is displayed in green.
- **ENTRY REJECTED**: No resident within the threshold distance was found. The face is classified as unknown and displayed in red.

**Q19. What happens when multiple faces are detected simultaneously?**  
Each face bounding box is processed independently through the encoding and matching pipeline. Each face gets its own gate decision — some may be ALLOWED (registered residents) and others REJECTED (unknown), all displayed simultaneously.

**Q20. Why is the resident database loaded into memory instead of querying SQLite for every frame?**  
Querying SQLite for every video frame (typically 25–30 frames per second) would create excessive I/O and latency. `SecurityRecognizer` loads all encodings once at startup and caches them in a Python list. Hot-reload (press `R`) re-queries the database without restarting. This keeps recognition latency under 50 ms per face.

---

## Section E – SQLite Database

**Q21. Why is SQLite used instead of MySQL or PostgreSQL?**  
SQLite is embedded (no server process), zero-configuration, and part of Python's standard library (`import sqlite3`). For a single-machine security gate with up to a few hundred residents, SQLite is simpler, faster to set up, and sufficiently performant. MySQL/PostgreSQL add network complexity and are better suited for multi-user, distributed applications.

**Q22. How are face encodings stored in SQLite?**  
The 128-D float32 numpy array is serialised to raw bytes using `.tobytes()` and stored as a BLOB (Binary Large Object). On retrieval, `numpy.frombuffer(blob, dtype=np.float32)` reconstructs the array exactly (lossless). This avoids JSON or CSV encoding overhead.

**Q23. What is a parameterized SQL query and why is it used?**  
A parameterized query uses `?` placeholders instead of string concatenation:
```python
cursor.execute("SELECT * FROM residents WHERE resident_id = ?", (rid,))
```
This prevents **SQL injection attacks** (malicious input cannot alter the query structure) and handles special characters automatically.

**Q24. What is the residents table schema?**  
```sql
CREATE TABLE residents (
    resident_id      TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    face_encoding    BLOB NOT NULL,
    registration_date TEXT NOT NULL
);
```

**Q25. How is duplicate detection handled?**  
`check_duplicate_resident(resident_id)` queries `SELECT 1 FROM residents WHERE resident_id = ?`. If a row is returned, the ID already exists. `add_resident()` calls this check before every INSERT and returns `False` without inserting if a duplicate is found.

---

## Section F – Evaluation Metrics

**Q26. Define True Positive, True Negative, False Positive and False Negative in this context.**  
- **TP**: System correctly grants ENTRY ALLOWED to a registered resident.
- **TN**: System correctly gives ENTRY REJECTED to an unregistered person.
- **FP**: System incorrectly grants ENTRY ALLOWED to an unregistered person (security breach).
- **FN**: System incorrectly gives ENTRY REJECTED to a registered resident (inconvenience).

**Q27. What is Accuracy and when is it misleading?**  
$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
Accuracy is misleading when classes are imbalanced — if 95% of people are unregistered, a system that always rejects everyone achieves 95% accuracy while being useless. Precision and Recall are more informative for imbalanced datasets.

**Q28. What is Precision and what does a low Precision mean for a security gate?**  
$$\text{Precision} = \frac{TP}{TP + FP}$$
Low Precision means many false alarms — intruders being incorrectly admitted. This is a critical security failure (false acceptance).

**Q29. What is Recall and what does low Recall mean for residents?**  
$$\text{Recall} = \frac{TP}{TP + FN}$$
Low Recall means registered residents are frequently rejected — causing frustration and defeating the purpose of the system (false rejection).

**Q30. What is the F1-score and when is it preferred?**  
$$F_1 = 2 \cdot \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
F1-score is the harmonic mean of Precision and Recall. It is preferred when there is a trade-off between the two. A high F1 means the system is both precise (few intruders admitted) and sensitive (few residents rejected).

**Q31. Explain the confusion matrix for this project.**  
```
              Predicted Rejected  Predicted Allowed
True Intruder       TN (88)           FP (0)
True Resident       FN (0)            TP (88)
```
All 88 genuine test samples (registered residents under 4 augmentations) were correctly allowed, and all 88 synthetic intruder samples were correctly rejected.

**Q32. Why are the evaluation results 100% and is this realistic?**  
The 100% result occurs because:
1. Genuine test samples are augmented variants of the same registered photos — the encoding pipeline is invariant to small augmentations.
2. Synthetic intruder encodings (random vectors) are very far (distance ~0.67) from any registered encoding — trivially rejected.
In real deployment, with actual photographs of different people, results will be lower, particularly for large angle changes or look-alike individuals.

---

## Section G – System Design

**Q33. How does the SecurityRecognizer cache work?**  
At `__init__`, it calls `get_all_residents()` which queries SQLite and deserialises all BLOB encodings. The list is stored in `self._residents`. Recognition loops over this in-memory list. The `reload_residents()` method re-queries the database — called when `R` is pressed in the live gate.

**Q34. What is the GATE IDLE state?**  
When no face is detected in the current frame, the system displays "GATE IDLE – AWAITING ENTRANT" in yellow, overlaid centrally on the video frame. No gate decision is made.

**Q35. How does threshold adjustment work in the live gate?**  
Pressing `+` increases `recognizer.threshold` by 0.05 (more lenient — more faces admitted). Pressing `-` decreases it by 0.05 (stricter — fewer faces admitted). The range is clamped to [0.10, 1.00]. The new threshold is applied immediately to subsequent frames without restarting.

---

*All answers reflect the actual implementation in this project.*
