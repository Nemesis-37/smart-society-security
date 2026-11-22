# Demonstration Guide – Smart Society Security System

## Prerequisites

- Python 3.13 installed at `C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe`
- Project folder: `c:\Users\DELL\OneDrive\Desktop\smart society security`
- Laptop webcam connected and enabled
- All packages installed (see `requirements.txt`)

---

## Quick Start (VS Code Terminal)

```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
python src/main.py
```

---

## Demo Script

### Step 1 – Show Registered Residents

From the main menu, choose **5 (View Registered Residents)**.

Expected output:
```
  22 registered resident(s):

  R001     Aarav Sharma
  R002     Priya Patel
  ...
  R022     Meera Nambiar
```

**What to explain:** The system stores 22 residents in a SQLite database. Each has a unique ID, name, and a 128-dimensional face encoding stored as a binary BLOB.

---

### Step 2 – Live Face Detection (Phase 4)

From the main menu, choose **2 (Live Webcam – Face Detection)**.

A window opens showing the webcam feed with:
- Green bounding boxes with corner accents around detected faces.
- Face count in the HUD.
- FPS display.
- "No face detected" message when no face is in frame.

**Demo actions:**
1. Hold your face in front of the camera → green box appears.
2. Hold up 2 fingers blocking one eye to test single-face detection.
3. Move away from camera → "No face detected" appears.
4. Press `Q` to exit.

---

### Step 3 – Security Gate (Phase 6)

From the main menu, choose **3 (Live Security Gate – Full Recognition)**.

**Expected behaviour:**

| Situation | Display |
|-----------|---------|
| No one in frame | GATE IDLE – AWAITING ENTRANT (yellow) |
| Registered resident | ENTRY ALLOWED (green) + resident name |
| Unregistered person | ENTRY REJECTED (red) + "Unknown Person" |

**Keyboard shortcuts to demonstrate:**
- `+` / `-` to adjust threshold live.
- `R` to reload the resident database.
- `Q` to exit.

**What to explain:** The system loads all 22 resident encodings at startup. For each webcam frame, it detects faces, generates HOG encodings, computes Euclidean distances to all stored encodings, and applies the 0.50 threshold.

---

### Step 4 – Register a New Resident (Phase 3)

From the main menu, choose **1 (Register a New Resident)**.

Then choose **2 (Upload from file)** and provide:
- Resident ID: `R099`
- Name: `Test Person`
- Photo path: a JPEG with a clear frontal face

**What to explain:** The system validates that exactly one face is detectable. It rejects photos with multiple faces, no faces, or low resolution. The face encoding is generated and stored with the metadata.

---

### Step 5 – Performance Evaluation (Phase 7)

From the main menu, choose **4 (Run Performance Evaluation)**.

Expected terminal output:
```
[Eval] Building genuine test samples from 22 residents…
[Eval] Generating 88 synthetic intruder samples…
[Eval] Dataset: 88 genuine + 88 intruder = 176 total samples.

  TP=88  TN=88  FP=0  FN=0
  Accuracy=100.0%  Precision=100.0%  Recall=100.0%  F1=100.0%
```

Output files in `evaluation_results/`:
- `confusion_matrix.png` – visual confusion matrix
- `environmental_robustness.png` – accuracy per test condition
- `threshold_analysis.png` – sensitivity curve
- `evaluation_summary.txt` – text report
- `test_results.csv` – raw per-sample results

---

### Step 6 – Run All Tests (Phase 8)

From the main menu, choose **6 (Run All Tests)**.

Expected: All tests pass across all 5 test modules.

---

## Running Tests Individually (PowerShell)

```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
python -u tests/test_database.py
python -u tests/test_registration.py
python -u tests/test_webcam.py
python -u tests/test_recognition.py
python -u tests/test_security_gate.py
```

---

## Git Push (after demo)

```powershell
cd "c:\Users\DELL\OneDrive\Desktop\smart society security"
git add .
git commit -m "Complete Smart Society Security System: Phases 1-8"
git branch -M main
git remote add origin https://github.com/Nemesis-37/smart-society-security.git
git push -u origin main
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera not opening | Run from VS Code terminal (not inside Antigravity sandbox) |
| `ModuleNotFoundError: src` | Run from project root: `cd "c:\...\smart society security"` |
| "No face detected" in registration | Use a clear frontal face photo with good lighting |
| Database is empty | Run `python -c "from src.register_faces import seed_20_residents; seed_20_residents()"` |
| `imshow` window not appearing | Run from a terminal; sandbox has no display |
