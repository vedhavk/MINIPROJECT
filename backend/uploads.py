"""
uploads.py
File-upload endpoint for registered farmers and veterinarians.

Flow:
1. JWT decoded → identify user role (farmer | veterinary)
2. checker.py validates and classifies the file (image | video)
3. predict.py runs the appropriate model
4. If prediction == 'diseased':
     - Alert record saved to alertcall_farmer / alertcall_veterinary
     - emails sent to ALL registered farmers AND vets (not just same pin_code)
5. Response returns prediction + alert status.
"""

import os
import logging
from pathlib import Path
from datetime import datetime

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException,
    UploadFile, status,
)
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import (
    get_db, Farmer, Veterinary,
    AlertCallFarmer, AlertCallVeterinary,
)
from checker import detect_file_type, validate_file_size
from predict import predict_image, predict_video, normalise_label
from alerts  import send_farmer_alert, send_vet_alert
from dotenv  import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

router     = APIRouter(prefix="/upload", tags=["Upload"])
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
MAX_MB     = int(os.getenv("MAX_FILE_SIZE_MB", 100))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/farmer/login")


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db:    Session = Depends(get_db),
) -> tuple:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role:  str = payload.get("role")
        if not email or role not in ("farmer", "veterinary"):
            raise exc
    except JWTError:
        raise exc

    user = (
        db.query(Farmer).filter(Farmer.email == email).first()
        if role == "farmer"
        else db.query(Veterinary).filter(Veterinary.email == email).first()
    )
    if user is None:
        raise exc
    return user, role


# ── Alert broadcast ───────────────────────────────────────────────────────────

def _broadcast_all(db: Session, latitude: float, longitude: float, pin_code: str):
    """
    Send alert emails to every registered farmer and veterinary in the DB.
    Returns dict with lists of successfully notified emails.
    """
    farmers = db.query(Farmer).all()
    vets    = db.query(Veterinary).all()

    log.info("Broadcasting disease alert to %d farmers and %d vets", len(farmers), len(vets))

    farmer_notified = []
    for f in farmers:
        try:
            ok = send_farmer_alert(f.email, f.name, latitude, longitude, pin_code)
            log.info("Farmer alert → %s: %s", f.email, "sent" if ok else "failed")
            if ok:
                farmer_notified.append(f.email)
        except Exception as e:
            log.error("Failed to send farmer alert to %s: %s", f.email, e)

    vet_notified = []
    for v in vets:
        try:
            ok = send_vet_alert(v.email, v.name, latitude, longitude, pin_code)
            log.info("Vet alert → %s: %s", v.email, "sent" if ok else "failed")
            if ok:
                vet_notified.append(v.email)
        except Exception as e:
            log.error("Failed to send vet alert to %s: %s", v.email, e)

    return {"farmers": farmer_notified, "vets": vet_notified}


# ── Upload endpoint ───────────────────────────────────────────────────────────

@router.post("/")
async def upload_file(
    file:      UploadFile = File(...),
    latitude:  float      = Form(...),
    longitude: float      = Form(...),
    pin_code:  str        = Form(...),
    auth:      tuple      = Depends(get_current_user),
    db:        Session    = Depends(get_db),
):
    user, role = auth
    log.info("Upload request from %s id=%s pin=%s", role, user.id, pin_code)

    # 1. Read + validate
    raw = await file.read()
    validate_file_size(raw, MAX_MB)

    # 2. Classify file type
    file_type = detect_file_type(file.filename, file.content_type)
    log.info("File type detected: %s (%s)", file_type, file.filename)

    # 3. Save file
    suffix    = Path(file.filename).suffix.lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    save_name = f"{role}_{user.id}_{timestamp}{suffix}"
    save_path = UPLOAD_DIR / save_name

    with open(save_path, "wb") as fh:
        fh.write(raw)
    log.info("Saved to %s (%d bytes)", save_path, len(raw))

    # 4. Run prediction
    if file_type == "image":
        result = predict_image(raw)
    else:
        result = predict_video(str(save_path))

    # Normalise label regardless of what model returns (0/1 or string)
    prediction = normalise_label(result["prediction"])
    confidence = result["confidence"]
    log.info("Prediction: %s (confidence: %s)", prediction, confidence)

    # 5. Trigger alerts if diseased
    alerts_sent = None

    if prediction == "diseased":
        log.info("DISEASED detected — saving alert record and sending emails")

        # Save alert record
        if role == "farmer":
            record = AlertCallFarmer(
                latitude   = latitude,
                longitude  = longitude,
                pin_code   = pin_code,
                farmer_id  = user.id,
                prediction = prediction,
                file_type  = file_type,
                alert_sent = "pending",
            )
        else:
            record = AlertCallVeterinary(
                latitude      = latitude,
                longitude     = longitude,
                pin_code      = pin_code,
                veterinary_id = user.id,
                prediction    = prediction,
                file_type     = file_type,
                alert_sent    = "pending",
            )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Send to ALL registered users
        alerts_sent = _broadcast_all(db, latitude, longitude, pin_code)

        # Update alert status
        total_sent = len(alerts_sent["farmers"]) + len(alerts_sent["vets"])
        record.alert_sent = "sent" if total_sent > 0 else "failed"
        db.commit()

        log.info(
            "Alert status: %s | farmers notified: %d | vets notified: %d",
            record.alert_sent,
            len(alerts_sent["farmers"]),
            len(alerts_sent["vets"]),
        )
    else:
        log.info("Prediction is healthy — no alerts sent")

    return {
        "filename":    save_name,
        "file_type":   file_type,
        "prediction":  prediction,
        "confidence":  confidence,
        "latitude":    latitude,
        "longitude":   longitude,
        "pin_code":    pin_code,
        "alerts_sent": alerts_sent,
    }