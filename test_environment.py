"""
Phase 1: Environment & Dependency Verification Script
Checks all required libraries, displays their versions, and verifies computer vision modules.
"""

import sys
import platform

print("=" * 60)
print("SMART SOCIETY SECURITY SYSTEM - ENVIRONMENT VERIFICATION")
print("=" * 60)

# System info
print(f"Operating System   : {platform.system()} {platform.release()} ({platform.architecture()[0]})")
print(f"Python Executable  : {sys.executable}")
print(f"Python Version     : {sys.version.split()[0]}")
print("-" * 60)

# Required libraries check
modules_to_test = [
    ("cv2", "OpenCV (Computer Vision)"),
    ("numpy", "NumPy (Numerical Operations)"),
    ("pandas", "Pandas (Data Management)"),
    ("sklearn", "Scikit-Learn (Metrics & Evaluation)"),
    ("matplotlib", "Matplotlib (Visualization & Plots)"),
    ("PIL", "Pillow (Image Processing)"),
    ("sqlite3", "SQLite3 (Database Management - Built-in)"),
]

all_passed = True
for mod_name, desc in modules_to_test:
    try:
        mod = __import__(mod_name)
        ver = getattr(mod, "__version__", "Standard Library")
        print(f"[PASSED] {desc:40} : v{ver}")
    except ImportError as e:
        print(f"[FAILED] {desc:40} : Import Error ({e})")
        all_passed = False

print("-" * 60)

# Special check for OpenCV face module & Haar Cascades
import cv2
has_face_module = hasattr(cv2, "face")
has_lbph = hasattr(cv2.face, "LBPHFaceRecognizer_create") if has_face_module else False
has_sface = hasattr(cv2, "FaceRecognizerSF")
has_yunet = hasattr(cv2, "FaceDetectorYN")
cascade_dir = cv2.data.haarcascades

print(f"OpenCV Face Module Installed        : {has_face_module}")
print(f"OpenCV LBPH Face Recognizer         : {has_lbph}")
print(f"OpenCV SFace Deep Recognizer        : {has_sface}")
print(f"OpenCV YuNet Deep Face Detector     : {has_yunet}")
print(f"Haar Cascades Available at          : {cascade_dir}")

# Check dlib and face_recognition status
print("-" * 60)
try:
    import dlib
    print("[INFO]   dlib is installed")
except ImportError:
    print("[INFO]   dlib is not installed (expected on Python 3.13 Windows - using OpenCV native engine)")

try:
    import face_recognition
    print("[INFO]   face_recognition is installed")
except ImportError:
    print("[INFO]   face_recognition is not installed (expected on Python 3.13 Windows - using OpenCV native engine)")

print("=" * 60)
if all_passed:
    print("STATUS: ENVIRONMENT IS 100% READY FOR PHASE 2!")
else:
    print("STATUS: ENVIRONMENT HAS MISSING DEPENDENCIES. PLEASE RESOLVE BEFORE PHASE 2.")
print("=" * 60)
