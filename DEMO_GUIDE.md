# Demonstration Guide – Smart Society Security System

**Course:** Computer Vision  
**System Version:** React + Vite Frontend · FastAPI Backend · OpenCV Pipeline · SQLite  
**Audience:** Project Evaluators & Course Examiners

---

## 1. Demonstration Setup & Prerequisites

Before starting the demonstration:
1. Ensure your laptop webcam is connected and enabled.
2. Confirm Python 3.13 is active: `python --version`.
3. Confirm Node.js is installed: `node -v`.

### Starting the Applications

Open two terminals in VS Code:

#### Terminal 1 — FastAPI Backend Server:
```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8088 --reload
```
*Verify that the terminal displays: `Application startup complete` on port 8088.*

#### Terminal 2 — React Web Dashboard:
```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security\frontend"
npm run dev
```
*Open `http://localhost:5180` in your browser.*

---

## 2. Step-by-Step Evaluator Walkthrough

### Step 1: Security Command Dashboard
1. Open `http://localhost:5180` in Google Chrome or Microsoft Edge.
2. Point out the **Header Telemetry**:
   - System Active indicator (green pulse).
   - Real-time digital clock.
3. Review the **Overview Metric Cards**:
   - **Active Residents:** Shows `22` (pulled dynamically from SQLite `database/society_security.db`).
   - **Database State:** `Connected`.
   - **Matching Threshold:** `0.50` (Euclidean distance cutoff).
   - **Model Accuracy:** `100.0%` (Phase 7 empirical test score).
4. Review the **Recently Registered Residents** section displaying live resident portraits and timestamps.

---

### Step 2: Resident Management & Dynamic Registration
1. In the sidebar, click **Residents** (`/residents`).
2. Show the **Search Bar**:
   - Type `"Aarav"` → instantly filters to Aarav Sharma (`R001`).
   - Type `"R005"` → instantly filters to Vikram Malhotra (`R005`).
   - Clear search → all 22 residents reappear.
3. Demonstrate **Adding a New Resident**:
   - Click the blue **Add Resident** button.
   - Enter Resident ID: `R023`.
   - Enter Full Name: `Test Entrant`.
   - Choose a photo containing a clear face.
   - Click **Register & Store**.
   - Show the validation feedback: The backend validates single-face presence using Haar Cascade, computes the 128-D spatial HOG vector, stores the JPEG in `dataset/residents/R023.jpg`, and writes the record into SQLite.
4. Demonstrate **Deleting a Resident**:
   - Click the trash icon next to `R023`.
   - Show the confirmation modal warning.
   - Confirm deletion → record and photo are cleanly removed.

---

### Step 3: Live Security Gate Interface
1. In the sidebar, click **Live Security Gate** (`/gate`).
2. Explain the **Security Decision Logic**:
   - **ENTRY ALLOWED (Green):** When a face matches a registered resident with Euclidean distance $\le \text{Threshold}$.
   - **ENTRY REJECTED (Red):** When a face exceeds the threshold or belongs to an unregistered visitor.
   - **GATE IDLE (Yellow):** When no face is in the camera view.
3. Click **Start Camera**:
   - The live MJPEG stream activates directly inside the dark security viewport.
   - As faces enter the camera view, the decision panel dynamically updates with:
     - Real-time decision badge (`ENTRY ALLOWED` vs. `ENTRY REJECTED`).
     - Entrant Name & Resident ID.
     - Exact face distance (e.g. `0.0790`).
     - Match confidence percentage.
4. Demonstrate **Real-Time Threshold Tuning**:
   - Move the slider from `0.50` to `0.30` (strict mode) or `0.70` (lenient mode).
   - Click **Save New Cutoff** → the backend recognition engine updates its parameter immediately without restart.
5. Click **Reload DB**:
   - Demonstrates hot-reloading resident encodings from SQLite into memory.
6. Click **Stop Camera**:
   - Demonstrates clean hardware resource release so the camera is never left locked.

---

### Step 4: Gate Entry & Access Audit Logs
1. In the sidebar, click **Entry Logs** (`/logs`).
2. Explain the **Event Throttling Mechanism**:
   - The system prevents frame-by-frame log flooding by implementing a 5-second cooldown per person.
   - Each logged entry contains: Log ID, Entrant Name, Resident ID, Verification Decision, Face Distance, and Timestamp.
3. Demonstrate **Filter & Search**:
   - Filter by `ENTRY ALLOWED` vs. `ENTRY REJECTED`.
   - Search by resident name.
   - Show pagination controls.

---

### Step 5: Model Evaluation Dashboard
1. In the sidebar, click **Evaluation** (`/evaluation`).
2. Explain the **Academic Methodology**:
   - Point out the **Academic Integrity Notice**: Explains that the 100% score comes from testing 88 genuine augmented variations + 88 synthetic random intruder vectors (176 total samples).
3. Review the **Binary Classification Breakdown**:
   - **True Positives (TP):** 88
   - **True Negatives (TN):** 88
   - **False Positives (FP):** 0
   - **False Negatives (FN):** 0
4. Switch between the **Matplotlib Benchmark Graphs**:
   - Click **Confusion Matrix Heatmap** → loads visual matrix.
   - Click **Environmental Robustness Bar Chart** → displays accuracy across Standard, Low Light, Angled, and Blurred conditions.
   - Click **Threshold Sensitivity Curve** → displays accuracy, precision, and recall across thresholds from 0.10 to 0.95.

---

### Step 6: Standalone Python CLI Demonstration (Alternative Mode)
To demonstrate that the core Python application remains 100% functional and uncompromised:
1. Open a new terminal and run:
   ```powershell
   python src/main.py
   ```
2. Press `5` to view all 22 registered residents in the terminal.
3. Press `3` to launch the native OpenCV security gate window.
4. Show keyboard shortcuts:
   - Press `+` / `-` to adjust threshold on the fly.
   - Press `R` to reload database.
   - Press `Q` to close the window.

---

## 3. Evaluator FAQ & Viva Defenses

| Examiner Question | Accurate Technical Answer |
|---|---|
| **Why is there no `dlib` or `face_recognition`?** | `dlib` has no official prebuilt wheels for Python 3.13 on Windows. This project implements a pure-OpenCV 128-D spatial gradient HOG encoder that is 100% native and requires no C++ build tools. |
| **Why is the evaluation accuracy 100%?** | The benchmark in `src/evaluate.py` tested 88 augmented variations of registered photos and 88 random intruder vectors. The random vectors have large Euclidean distance ($\approx 0.67$), making them easily rejectable at threshold $0.50$. In real-world unconstrained deployments, accuracy would be lower. |
| **How does video streaming work without WebSockets?** | We use HTTP Multipart MJPEG streaming (`multipart/x-mixed-replace`) via FastAPI's `StreamingResponse`. The browser renders it natively inside a standard `<img>` tag with minimal CPU overhead. |
| **How are face encodings stored in SQLite?** | They are stored as raw 512-byte binary BLOBs using `numpy.ndarray.tobytes()`, providing 100% exact float32 vector reconstruction via `numpy.frombuffer()`. |
| **How are duplicate logs prevented during video streaming?** | The `CameraManager` maintains an in-memory timestamp dictionary with a 5-second cooldown per resident/visitor to prevent continuous frame insertion into SQLite. |
