# Smart Society Security System

> **College Computer Vision Project** – Python 3.13 · OpenCV · FastAPI · React + Vite · SQLite  
> Complete end-to-end facial verification access-control system with modern dark web dashboard and CLI interface.

---

## 1. Project Overview

> **Academic Prototype & Privacy Notice:**  
> This system is an educational prototype developed for a college Computer Vision coursework demonstration. It is **not** intended for mission-critical, enterprise, or production security infrastructure. All pre-seeded resident photos in `dataset/residents/` are synthetically generated from public-domain sample reference imagery (Grace Hopper, Matplotlib sample dataset) and do not contain private biometric data of actual residents. Always obtain explicit informed consent before capturing and registering live personal photographs.

The **Smart Society Security System** is a real-time face-recognition access-control platform that:

- Registers residents with their photographs via live webcam capture or photo upload.
- Stores resident records, reference portraits, and 128-D face encodings in a local **SQLite** database.
- Streams live video from a laptop webcam using **OpenCV** with real-time HUD overlays.
- Detects faces using **Haar Cascade** classifiers and generates gradient-based 128-D spatial HOG encodings.
- Grants **ENTRY ALLOWED** (green) to registered residents or **ENTRY REJECTED** (red) to unknown visitors.
- Records authentic gate verification decisions into an SQLite audit log (`entry_logs`) with cooldown throttling.
- Evaluates performance with empirical metrics: Accuracy, Precision, Recall, F1-score, and Confusion Matrix.
- Provides both an interactive **React + Vite Dark Dashboard** and a standalone **OpenCV Python CLI**.

---

## 2. System Architecture

```text
                                 +--------------------------------+
                                 |  React + Vite Frontend (5173)  |
                                 +---------------+----------------+
                                                 | (Axios & MJPEG Stream)
                                                 v
                                 +---------------+----------------+
                                 |     FastAPI Backend (8000)     |
                                 +-------+---------------+--------+
                                         |               |
                    +--------------------+               +-------------------+
                    v                                                        v
      +-------------+------------+                             +-------------+------------+
      |  CameraManager Singleton |                             |   SQLite Database Layer  |
      +-------------+------------+                             | (society_security.db)    |
                    |                                          +-------------+------------+
                    v                                                        |
      +-------------+------------+                                           v
      |   SecurityRecognizer     | <-----------------------------------------+
      |  (128-D HOG + Euclidean) |   (In-Memory Resident Encodings Cache)
      +-------------+------------+
```

---

## 3. Project Directory Structure

```text
smart society security/
├── frontend/                          # React + Vite Web Dashboard
│   ├── package.json                   # React 18, Tailwind CSS, Lucide React, Recharts, Axios
│   ├── vite.config.js                 # Dev server port 5173
│   ├── tailwind.config.js             # Custom dark navy theme
│   └── src/
│       ├── components/                # Reusable UI (Sidebar, Header, StatCards, Modals)
│       ├── pages/                     # Dashboard, Residents, LiveGate, EntryLogs, Evaluation, Settings
│       └── services/api.js            # Axios client communicating with FastAPI
├── backend/                           # FastAPI Backend Integration Layer
│   └── app/
│       ├── main.py                    # FastAPI application & CORS middleware
│       ├── camera_manager.py          # Thread-safe Singleton camera loop & throttled logging
│       ├── config.py                  # Project paths
│       ├── schemas.py                 # Pydantic request/response models (vector protection)
│       └── api/routes/                # Health, Dashboard, Residents, Gate, Logs, Evaluation
├── src/                               # Canonical Core Python Modules
│   ├── database.py                   # SQLite database CRUD operations
│   ├── face_recognition.py           # Haar Cascade detection & 128-D spatial HOG encoder
│   ├── register_faces.py             # Single-face validation, webcam & file registration
│   ├── webcam_detection.py           # Real-time webcam capture, bounding boxes & HUD
│   ├── recognition_engine.py         # SecurityRecognizer class & in-memory resident matching
│   ├── security_gate.py              # Live gate loop with OpenCV display window
│   ├── evaluate.py                   # Evaluation harness, metric computation, graph generation
│   └── main.py                       # CLI master menu launcher
├── database/
│   └── society_security.db           # SQLite database (residents & entry_logs tables)
├── dataset/
│   ├── residents/                    # Resident reference photos (R001.jpg – R022.jpg)
│   └── unknown/                      # Unregistered visitor photo buffer
├── evaluation_results/                # Benchmark plots & performance summary
│   ├── confusion_matrix.png
│   ├── environmental_robustness.png
│   ├── threshold_analysis.png
│   ├── evaluation_summary.txt
│   └── test_results.csv
├── tests/                             # Automated Test Suites (41 tests passing)
│   ├── test_database.py              # SQLite CRUD tests
│   ├── test_registration.py          # Registration & photo validation tests
│   ├── test_webcam.py                # Headless camera & HUD tests
│   ├── test_recognition.py           # Face matching & resident cache tests
│   ├── test_security_gate.py         # End-to-end security gate tests
│   ├── test_evaluation.py            # Evaluation metric bounds tests
│   └── test_fastapi.py               # FastAPI integration & API tests
├── requirements.txt                   # Pinned Python dependencies
├── PROJECT_REPORT.md                  # Comprehensive academic report
├── VIVA_QUESTIONS.md                  # 35 viva questions & detailed answers
└── DEMO_GUIDE.md                      # Step-by-step evaluator presentation guide
```

---

## 4. Dependencies & Prerequisites

- **Python 3.13** (64-bit Windows)
- **Node.js 18+** & **npm**
- Laptop webcam (built-in or USB)

### Python Dependencies (`requirements.txt`)

```text
opencv-contrib-python==5.1.0
numpy==2.4.4
Pillow==11.2.1
pandas==3.0.2
scikit-learn==1.9.1
matplotlib==3.11.2
tqdm==4.67.3
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
python-multipart>=0.0.9
pydantic>=2.8.0
```

> **Note on `dlib` & `face_recognition`:**  
> Python 3.13 on Windows does not support `dlib` or `face_recognition` due to missing prebuilt wheels. This project implements a custom pure-OpenCV 128-D spatial gradient HOG encoder that runs natively on Python 3.13 without C++ build tools.

---

## 5. Quick Start Instructions

### Mode A: React Frontend + FastAPI Backend (Web Dashboard)

Open two terminal windows in VS Code:

#### Terminal 1 — Start FastAPI Backend:
```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8088 --reload
```
*API interactive documentation will be available at: `http://127.0.0.1:8088/docs`.*

#### Terminal 2 — Start React Frontend:
```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security\frontend"
npm install
npm run dev
```
*Open your browser and navigate to: `http://localhost:5180`.*

---

### Mode B: Standalone OpenCV CLI Application

To run the standalone desktop interface without opening a browser:

```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
python src/main.py
```

Menu options:
- `1`: Register a New Resident (webcam or photo upload)
- `2`: Live Webcam Face Detection Only
- `3`: Live Security Gate (Full Face Recognition)
- `4`: Run Model Evaluation
- `5`: View Registered Residents
- `6`: Run All Automated Tests

---

## 6. API Reference Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health & database connectivity check |
| `GET` | `/api/dashboard/stats` | Active residents count, DB status, accuracy |
| `GET` | `/api/residents` | List all residents (zero biometric vector leakage) |
| `GET` | `/api/residents/{id}/photo` | Serves reference portrait for resident |
| `POST` | `/api/residents` | Register resident (multipart upload with face validation) |
| `DELETE` | `/api/residents/{id}` | Delete resident record and photo |
| `POST` | `/api/gate/start` | Starts the camera capture and recognition loop |
| `POST` | `/api/gate/stop` | Stops camera and releases hardware resources |
| `GET` | `/api/gate/status` | Live camera state, FPS, entrant decision, face count |
| `GET` | `/api/gate/stream` | Real-time MJPEG live stream with HUD overlays |
| `POST` | `/api/gate/threshold` | Update Euclidean match cutoff ($0.10 - 0.95$) |
| `POST` | `/api/gate/reload` | Hot-reload resident database into memory |
| `GET` | `/api/logs` | Real gate entry audit logs (search, status filter, pagination) |
| `GET` | `/api/evaluation/summary` | Summary evaluation metrics ($TP, TN, FP, FN$, accuracy) |
| `GET` | `/api/evaluation/plot/{name}` | Serves Matplotlib evaluation charts |

---

## 7. Running Automated Tests

Run the full automated test suite (41 tests):

```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
python -u tests/test_database.py
python -u tests/test_registration.py
python -u tests/test_webcam.py
python -u tests/test_recognition.py
python -u tests/test_security_gate.py
python -u tests/test_fastapi.py
```

---

## 8. Limitations & Academic Scope

1. **Controlled Evaluation Metrics:** The reported 100% evaluation accuracy was achieved in a controlled benchmark testing 22 residents under 4 augmentation conditions plus 88 synthetic random intruder vectors. Real-world human intruders in unconstrained environments will yield lower accuracy.
2. **Lighting & Pose Sensitivity:** The Haar Cascade detector and HOG gradient pipeline perform best on frontal faces ($< 25^\circ$ head rotation) and require adequate illumination ($> 50\text{ lux}$).
3. **Single Camera Hardware:** Windows restricts physical webcam access to one process at a time. The `CameraManager` singleton ensures clean acquisition and release.
