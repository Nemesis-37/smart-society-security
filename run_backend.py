"""
run_backend.py
Simple launcher for the Smart Society Security FastAPI backend.
Listens on port 8088 on all local interfaces (0.0.0.0).
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting Smart Society Security System Backend")
    print("  URL: http://127.0.0.1:8088")
    print("  API Docs: http://127.0.0.1:8088/docs")
    print("=" * 60)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8088, reload=True)
