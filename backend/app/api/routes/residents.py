"""
backend/app/api/routes/residents.py
Resident Management Endpoints.
Reuses src.database and src.register_faces.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from typing import List
import os
import cv2
import numpy as np
from backend.app.schemas import ResidentResponse, ResidentRegisterResponse
from backend.app.config import RESIDENTS_DIR
from src.database import (
    get_all_residents,
    get_resident_by_id,
    delete_resident,
    check_duplicate_resident,
    DEFAULT_DB_PATH,
)
from src.register_faces import register_resident_image

router = APIRouter(prefix="/residents", tags=["Residents"])


@router.get("", response_model=List[ResidentResponse])
def list_residents():
    """
    Returns all registered residents from SQLite.
    Face encoding binary BLOBs are completely excluded to protect privacy.
    """
    raw = get_all_residents(str(DEFAULT_DB_PATH))
    results = []
    for r in raw:
        rid = r["resident_id"]
        results.append(
            ResidentResponse(
                resident_id=rid,
                name=r["name"],
                registration_date=r["registration_date"],
                photo_url=f"/api/residents/{rid}/photo",
            )
        )
    return results


@router.get("/{resident_id}/photo")
def get_resident_photo(resident_id: str):
    """
    Serves the resident's reference photo from dataset/residents/<ID>.jpg.
    """
    clean_id = str(resident_id).strip().upper()
    photo_path = os.path.join(RESIDENTS_DIR, f"{clean_id}.jpg")
    if not os.path.exists(photo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photograph for resident {clean_id} not found on disk.",
        )
    return FileResponse(photo_path, media_type="image/jpeg")


@router.post("", response_model=ResidentRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_resident(
    resident_id: str = Form(..., description="Unique ID, e.g. R023"),
    name: str = Form(..., description="Full Name"),
    photo: UploadFile = File(..., description="JPEG/PNG image containing a clear single face"),
):
    """
    Registers a new resident by validating single face presence,
    storing the photo, and persisting the 128-D encoding into SQLite.
    Reuses existing src.register_faces.register_resident_image.
    """
    clean_id = str(resident_id).strip().upper()
    clean_name = str(name).strip()

    if not clean_id or not clean_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resident ID and Name cannot be empty.",
        )

    # Duplicate check
    if check_duplicate_resident(clean_id, str(DEFAULT_DB_PATH)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Resident ID '{clean_id}' already exists in the database.",
        )

    # Validate file type
    if photo.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Please upload a JPEG or PNG photograph.",
        )

    # Read uploaded bytes into numpy/cv2 image
    contents = await photo.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image file size exceeds maximum limit of 10MB.",
        )

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None or image.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode image file.",
        )

    # Call canonical registration function
    success, msg = register_resident_image(
        image=image,
        resident_id=clean_id,
        name=clean_name,
        db_path=str(DEFAULT_DB_PATH),
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=msg,
        )

    return ResidentRegisterResponse(
        success=True,
        message=msg,
        resident_id=clean_id,
        name=clean_name,
    )


@router.delete("/{resident_id}")
def remove_resident(resident_id: str):
    """
    Deletes a resident from SQLite and removes their reference photo from dataset/residents/.
    """
    clean_id = str(resident_id).strip().upper()
    existing = get_resident_by_id(clean_id, str(DEFAULT_DB_PATH))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident '{clean_id}' not found in database.",
        )

    deleted = delete_resident(clean_id, str(DEFAULT_DB_PATH))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resident from database.",
        )

    # Clean up photograph file if present
    photo_path = os.path.join(RESIDENTS_DIR, f"{clean_id}.jpg")
    if os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except Exception:
            pass

    return {
        "success": True,
        "message": f"Resident {clean_id} ('{existing['name']}') deleted successfully.",
        "resident_id": clean_id,
    }
