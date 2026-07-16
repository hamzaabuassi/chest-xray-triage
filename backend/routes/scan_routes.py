from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from PIL import Image
import io
from database import get_db
import models
from auth import get_current_user
from ml.inference import run_inference

router = APIRouter()


# ---- Response schemas ----
class ScanResponse(BaseModel):
    id: int
    prediction: str
    confidence: float
    risk_tier: str
    original_image_path: str
    gradcam_image_path: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Predict endpoint ----
@router.post("/predict", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="File must be a JPEG or PNG image")

    try:
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    result = run_inference(image)

    scan = models.Scan(
        user_id=current_user.id,
        original_image_path=result["original_image_path"],
        gradcam_image_path=result["gradcam_image_path"],
        prediction=result["prediction"],
        confidence=result["confidence"],
        risk_tier=result["risk_tier"],
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return scan


# ---- History endpoint ----
@router.get("/history", response_model=list[ScanResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    scans = (
        db.query(models.Scan)
        .filter(models.Scan.user_id == current_user.id)
        .order_by(models.Scan.created_at.desc())
        .all()
    )
    return scans


# ---- Single scan detail ----
@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    scan = (
        db.query(models.Scan)
        .filter(models.Scan.id == scan_id, models.Scan.user_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


# ---- Delete scan ----
@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    scan = (
        db.query(models.Scan)
        .filter(models.Scan.id == scan_id, models.Scan.user_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    db.delete(scan)
    db.commit()
    return None