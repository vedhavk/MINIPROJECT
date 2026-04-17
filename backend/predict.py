import io
import os

# Reduce TensorFlow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import cv2
import numpy as np
import joblib
import logging
import warnings
from pathlib import Path
from fastapi import HTTPException

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

# TF 2.17.0 — use tensorflow.keras only, never standalone keras
import tensorflow as tf
from tensorflow.keras.models import load_model

logger.info(f"TensorFlow version: {tf.__version__}")

# ─────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────
_keras_model   = None
_sklearn_model = None

BASE_DIR = Path(__file__).resolve().parent

KERAS_MODEL_PATH   = BASE_DIR / "img.keras"
SKLEARN_MODEL_PATH = BASE_DIR / "vo.pkl"

IMG_SIZE = (224, 224)

# Label order must match training:
#   class_indices = {"diseased": 0, "healthy": 1}
#   sigmoid output → P(class_index == 1) → P(healthy)
CLASS_NAMES = ["diseased", "healthy"]   # index 0 → diseased, index 1 → healthy

# ─────────────────────────────────────────────
# LOAD IMAGE MODEL
# ─────────────────────────────────────────────
def _load_keras():
    global _keras_model

    if _keras_model is None:
        if not KERAS_MODEL_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Model not found at {KERAS_MODEL_PATH}"
            )

        try:
            _keras_model = load_model(
                str(KERAS_MODEL_PATH),
                compile=False
            )
            logger.info(f"Model loaded from {KERAS_MODEL_PATH}")
            logger.info(f"  Input  shape: {_keras_model.input_shape}")
            logger.info(f"  Output shape: {_keras_model.output_shape}")

        except Exception as e:
            logger.exception("Model load failed")
            raise HTTPException(
                status_code=500,
                detail=f"Model load error: {e}"
            )

    return _keras_model

# ─────────────────────────────────────────────
# LOAD VIDEO MODEL
# ─────────────────────────────────────────────
def _load_sklearn():
    global _sklearn_model

    if _sklearn_model is None:
        if not SKLEARN_MODEL_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Sklearn model not found at {SKLEARN_MODEL_PATH}"
            )

        try:
            _sklearn_model = joblib.load(str(SKLEARN_MODEL_PATH))
            logger.info("Sklearn model loaded")

            # Log expected feature count for debugging
            n = getattr(_sklearn_model, "n_features_in_", None)
            logger.info(f"  Sklearn model expects {n} features")

        except Exception as e:
            logger.exception("Sklearn load failed")
            raise HTTPException(
                status_code=500,
                detail=f"Sklearn model load error: {e}"
            )

    return _sklearn_model

# ─────────────────────────────────────────────
# IMAGE PROCESSING
# ─────────────────────────────────────────────
def _decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is not None:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Fallback: PIL handles more formats
    from PIL import Image
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(pil_img)


def _preprocess_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decodes → resizes to 224×224 → normalises to [0, 1] → adds batch dim.
    Returns shape (1, 224, 224, 3).
    """
    img = _decode_image_bytes(image_bytes)
    img = cv2.resize(img, IMG_SIZE, interpolation=cv2.INTER_LANCZOS4)
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)   # (1, 224, 224, 3)

# ─────────────────────────────────────────────
# VIDEO PROCESSING
# ─────────────────────────────────────────────
def _extract_video_feature_vector(video_path: str, n_features: int) -> np.ndarray:
    """
    Extracts a feature vector from a video to match what the model was trained on.

    Strategy auto-selects based on n_features:
      n_features == 20  → 10 frames × [mean, std] of grayscale pixels  (20 features)
      n_features == 30  → 10 frames × [mean, std, median]              (30 features)
      n_features == 40  → 10 frames × [mean, std, min, max]            (40 features)
      anything else     → falls back to 20-feature extraction with a warning
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Could not open video")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
    n_sample_frames = 10
    indices = np.linspace(0, max(total_frames - 1, 0), n_sample_frames, dtype=int)

    frames_gray = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()

        if not ret or frame is None:
            # Use a black frame as fallback so vector length stays consistent
            frame = np.zeros((64, 64, 3), dtype=np.uint8)

        frame_resized = cv2.resize(frame, (64, 64))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY).astype("float32") / 255.0
        frames_gray.append(gray.flatten())   # 64×64 = 4096 values per frame

    cap.release()

    # ── Choose stat extraction based on expected feature count ──────────────
    if n_features == 20:
        # 10 frames × 2 stats = 20
        features = []
        for f in frames_gray:
            features.extend([f.mean(), f.std()])

    elif n_features == 30:
        # 10 frames × 3 stats = 30
        features = []
        for f in frames_gray:
            features.extend([f.mean(), f.std(), float(np.median(f))])

    elif n_features == 40:
        # 10 frames × 4 stats = 40
        features = []
        for f in frames_gray:
            features.extend([f.mean(), f.std(), f.min(), f.max()])

    elif n_features == 60:
        # 10 frames × 6 stats = 60
        features = []
        for f in frames_gray:
            features.extend([
                f.mean(), f.std(), float(np.median(f)),
                f.min(), f.max(), float(np.percentile(f, 75) - np.percentile(f, 25))
            ])

    else:
        # Unknown n_features — warn and default to 20-feature extraction
        logger.warning(
            f"Unexpected n_features={n_features}. "
            f"Defaulting to 20-feature extraction (mean+std per frame). "
            f"If prediction fails, retrain the model or adjust extraction to match."
        )
        features = []
        for f in frames_gray:
            features.extend([f.mean(), f.std()])

    vector = np.array(features, dtype="float32")
    logger.info(f"Extracted video feature vector of shape {vector.shape}")
    return vector.reshape(1, -1)

# ─────────────────────────────────────────────
# PREDICT IMAGE
# ─────────────────────────────────────────────
def predict_image(image_bytes: bytes):
    """
    Binary sigmoid model:
      output neuron = P(healthy)   [label index 1]
      prob >= 0.5  → healthy
      prob <  0.5  → diseased
      confidence   = distance from 0.5, mapped to [0.5, 1.0]
    """
    try:
        model  = _load_keras()
        tensor = _preprocess_image_bytes(image_bytes)
        preds  = model.predict(tensor, verbose=0)   # shape (1, 1)

        if preds.shape[-1] == 1:
            # ── Binary sigmoid output ─────────────────────────
            prob = float(preds[0][0])          # P(healthy)

            if prob >= 0.5:
                label      = "healthy"
                confidence = prob
            else:
                label      = "diseased"
                confidence = 1.0 - prob        # P(diseased)

        else:
            # ── Softmax fallback (multi-class) ────────────────
            idx        = int(np.argmax(preds[0]))
            label      = CLASS_NAMES[idx]
            confidence = float(preds[0][idx])

        return {
            "prediction": label,
            "confidence": round(confidence, 4)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Image prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# PREDICT VIDEO
# ─────────────────────────────────────────────
def predict_video(video_path: str):
    try:
        model      = _load_sklearn()
        n_features = getattr(model, "n_features_in_", 20)   # default 20 if not set
        features   = _extract_video_feature_vector(video_path, n_features)

        # Safety check before calling model
        if features.shape[1] != n_features:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Feature mismatch: extracted {features.shape[1]} features "
                    f"but model expects {n_features}. "
                    f"Check _extract_video_feature_vector logic."
                )
            )

        pred = model.predict(features)[0]

        # Confidence via predict_proba if available
        confidence = 1.0
        if hasattr(model, "predict_proba"):
            try:
                proba      = model.predict_proba(features)[0]
                confidence = round(float(proba.max()), 4)
            except Exception:
                pass  # not all pipelines support predict_proba after transforms

        return {
            "prediction": str(pred).lower(),
            "confidence": confidence
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Video prediction failed")
        raise HTTPException(status_code=500, detail=str(e))