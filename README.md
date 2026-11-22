# Smart Society Security System – Face Recognition Access Control

An end-to-end, real-time Computer Vision security access control system developed with **Python**, **OpenCV**, and **SQLite**. The system monitors live webcam feeds at a residential society gate, detects human faces, computes normalized 128-dimensional face encoding vectors, and performs identity verification against a database of registered residents.

* **Recognized Residents:** Displays a **Green** bounding box with **`ENTRY ALLOWED`**, resident name, ID, distance, and confidence score.
* **Unregistered Visitors / Intruders:** Displays a **Red** bounding box with **`ENTRY REJECTED`** and **`Unknown Person`** label.

---

## Key Features

1. **Pure Native OpenCV & NumPy Engine:**
   - 100% compatible with modern **Python 3.13 on Windows 11**.
   - Zero compilation bottlenecks: does not require MSVC C++ Build Tools or unsupported dlib wheels.
2. **Robust Face Detection:**
   - Pre-trained OpenCV Haar Feature-based Cascade Classifier (`haarcascade_frontalface_default.xml`).
   - Histogram equalization to reliably detect faces under varying ambient light.
3. **128-Dimensional Face Encodings:**
   - Canonical 100×100 spatial alignment with CLAHE (Contrast-Limited Adaptive Histogram Equalization).
   - 4×4 spatial anatomical grid pooling with 8-orientation Sobel gradient filters.
   - Global $L_2$ unit-hypersphere normalization.
4. **SQLite Database Layer:**
   - Stores `resident_id`, `name`, binary `face_encoding` BLOBs, and timestamps.
   - Exact float32 vector serialization/deserialization with zero numerical drift.
   - Duplicate ID detection and transaction safety.
5. **Real-time Live Webcam Interface:**
   - Live video stream with heads-up display (HUD), FPS meter, and active resident count.
   - Real-time threshold tuning directly from the keyboard (`+` / `-`).
   - Hot-reload resident database without restarting (`r`).
   - Multi-face support and graceful handling of frames without faces.
6. **Academic Performance Evaluation:**
   - Rigorous benchmarking on an unseen evaluation dataset across varied environmental conditions (lighting, angle, blur).
   - Confusion matrix, Accuracy, Precision, Recall, F1-Score, and sensitivity plots.

---

## Project Structure

```text
smart society security/
├── database/
│   ├── __init__.py
│   └── db_manager.py           # SQLite connection, schema initialization & CRUD
├── models/
│   ├── __init__.py
│   ├── face_pipeline.py        # Haar detection, CLAHE, 128-D encoding & ROI extraction
│   └── recognizer.py           # Distance metric, threshold tuning & decision engine
├── data/
│   ├── society_security.db     # SQLite database file
│   └── registered_faces/       # Resident portrait archive (22+ residents)
├── tests/
│   ├── __init__.py
│   ├── test_db.py              # Phase 2 database unit tests
│   ├── test_phase3.py          # Phase 3 registration & photo validation tests
│   ├── test_phase4.py          # Phase 4 webcam integration tests
│   ├── test_phase5.py          # Phase 5 face recognition & distance tests
│   └── test_phase6.py          # Phase 6 full end-to-end integration tests
├── evaluation_results/
│   ├── confusion_matrix.png    # Matplotlib confusion matrix heatmap
│   ├── environmental_robustness.png # Lighting, angle, and blur performance chart
│   ├── threshold_analysis.png  # Threshold sensitivity curve
│   └── evaluation_summary.txt  # Quantitative benchmark summary
├── main.py                     # Master application menu & launcher
├── society_security_system.py  # Standalone live OpenCV security gate application
├── register_resident.py        # Interactive resident registration CLI (webcam / upload)
├── seed_residents.py           # Batch seed script for 22 default residents
├── evaluate_system.py          # Academic benchmark & evaluation suite
├── requirements.txt            # Dependency specification
├── .gitignore                  # Git exclusion rules
├── PROJECT_REPORT.md           # Comprehensive college project report
├── VIVA_QUESTIONS.md           # 30+ Viva questions and answers
└── DEMO_GUIDE.md               # Step-by-step live demonstration script
```

---

## Installation & Setup

### 1. Prerequisites
* **Operating System:** Windows 10 / 11 (64-bit)
* **Python Version:** Python 3.10 to 3.13 (Python 3.13.7 verified)
* **Hardware:** Laptop with integrated webcam or external USB camera

### 2. Install Required Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```powershell
pip install -r requirements.txt
```

### 3. Verify Environment
Run the automated environment check:
```powershell
python test_environment.py
```

---

## How to Run

### Option 1: Master Application Menu (Recommended)
Launch the unified master menu:
```powershell
python main.py
```
From the interactive menu:
* Press `1` to launch the **Live Security Gate System**.
* Press `2` to open the **Resident Registration System**.
* Press `3` to view the **Registered Residents Directory**.
* Press `4` to execute **Full System Diagnostics**.
* Press `5` to exit.

---

### Option 2: Live Security Gate Directly
Launch the real-time webcam security window directly:
```powershell
python society_security_system.py
```

#### Keyboard Shortcuts during Live Video:
| Key | Action |
| :--- | :--- |
| **`q`** or **`[ESC]`** | Close webcam window and exit cleanly |
| **`+`** or **`=`** | Increase matching distance threshold (+0.02) |
| **`-`** or **`_`** | Decrease matching distance threshold (-0.02) |
| **`r`** or **`R`** | Reload resident database from SQLite |

---

### Option 3: Register a New Resident
To register yourself or another resident:
```powershell
python register_resident.py
```
* **Mode 1 (Webcam Capture):** Opens the live camera feed with a green alignment box. Press **`s`** or **`[SPACE]`** to capture your photograph when your face is centered.
* **Mode 2 (File Upload):** Enter the path to any existing portrait photo (`.jpg`, `.png`).

---

### Option 4: Run Academic Benchmark & Generate Graphs
To evaluate the system against unseen test data and generate performance graphs:
```powershell
python evaluate_system.py
```
Generated graphs and reports are saved to [evaluation_results/](file:///c:/Users/DELL/OneDrive/Desktop/smart society security/evaluation_results/).

---

### Option 5: Run Automated Unit Tests
To run all test suites across all phases:
```powershell
python -u tests/test_db.py
python -u tests/test_phase3.py
python -u tests/test_phase4.py
python -u tests/test_phase5.py
python -u tests/test_phase6.py
```

---

## Core Technologies & Libraries

* **OpenCV (`opencv-contrib-python` v5.1.0):** Image processing, Haar Cascade face detection, spatial filtering, CLAHE, affine transformations, and high-performance GUI rendering.
* **NumPy (v2.4.4):** High-dimensional array manipulations, gradient operations, vector norms, and serialization.
* **SQLite3:** Embedded relational database storing resident credentials and 128-D float32 encoding BLOBs.
* **Scikit-Learn (v1.9.1):** Confusion matrix computation, Accuracy, Precision, Recall, and F1-score evaluation.
* **Matplotlib (v3.11.2):** High-resolution performance visualization, confusion matrix heatmaps, and threshold sensitivity curves.
* **Pandas (v3.0.2):** Performance breakdown across environmental conditions.

---

## License & Ethics Notice
* **Academic Prototype:** Designed for educational and laboratory evaluation.
* **Ethical Use:** Always obtain consent before capturing or storing photographs of individuals for facial recognition testing.
