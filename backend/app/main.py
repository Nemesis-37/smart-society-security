"""
backend/app/main.py
FastAPI Application Entry Point.
Configures CORS, routers, and health checks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.config import CORS_ORIGINS
from backend.app.api.routes import health, dashboard, residents, gate, evaluation, logs

app = FastAPI(
    title="Smart Society Security System API",
    description="FastAPI Backend integration layer for OpenCV Face Recognition & SQLite",
    version="1.0.0",
)

# Configure CORS for React Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(residents.router, prefix="/api")
app.include_router(gate.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(logs.router, prefix="/api")


@app.get("/")
def root():
    return {
        "system": "Smart Society Security System API",
        "status": "Online",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8088, reload=True)
