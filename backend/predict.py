<<<<<<< HEAD
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
=======
"""
predict.py
Runs inference on duck health files.

- Image  -> best_model(3).keras   (TensorFlow / Keras CNN)
- Video  -> duck_classifier.pkl   (scikit-learn SVM)

The SVM was trained on a feature vector of exactly 16488 values.
We reproduce that by: sampling frames, resizing to 62x88 (= 5496px RGB
per frame * 3 frames = 16488), flattening and concatenating.
But since the exact training pipeline is unknown, we dynamically
adapt the resize so the output always matches n_features_in_ from the model.
"""

import os
import cv2
import numpy as np
import joblib
from pathlib import Path
from fastapi import HTTPException

_keras_model   = None
_sklearn_model = None

MODEL_DIR          = Path(os.getenv("MODEL_DIR", "."))
KERAS_MODEL_PATH   = MODEL_DIR / "best_model(3).keras"
SKLEARN_MODEL_PATH = MODEL_DIR / "duck_classifier.pkl"

IMG_SIZE = (224, 224)


def _load_keras():
    global _keras_model
    if _keras_model is None:
        if not KERAS_MODEL_PATH.exists():
            raise HTTPException(status_code=500,
                detail=f"Keras model not found at {KERAS_MODEL_PATH}")
        import tensorflow as tf
        _keras_model = tf.keras.models.load_model(str(KERAS_MODEL_PATH))
    return _keras_model


def _load_sklearn():
    global _sklearn_model
    if _sklearn_model is None:
        if not SKLEARN_MODEL_PATH.exists():
            raise HTTPException(status_code=500,
                detail=f"sklearn model not found at {SKLEARN_MODEL_PATH}")
        _sklearn_model = joblib.load(str(SKLEARN_MODEL_PATH))
    return _sklearn_model


def _preprocess_image_bytes(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, IMG_SIZE)
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)


def _extract_video_feature_vector(video_path: str, n_features: int) -> np.ndarray:
    """
    Extract frames from video and produce a flat vector of exactly n_features.

    Strategy:
    1. Figure out how many frames and what frame size gives n_features pixels.
    2. Sample that many frames evenly, resize each, flatten & concatenate.
    3. If we can't find a clean split, sample 1 frame and resize to fit exactly.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Could not open video file.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        total_frames = 100  # fallback estimate

    # ── Find a (n_frames, height, width, channels) that matches n_features ──
    # Try common frame counts; prefer RGB (3 channels) then grayscale (1)
    best = None
    for n_frames in [1, 2, 4, 5, 6, 8, 10, 12, 16, 20, 24, 30, 32]:
        for channels in [3, 1]:
            px_per_frame = n_features / (n_frames * channels)
            if px_per_frame != int(px_per_frame):
                continue
            px_per_frame = int(px_per_frame)
            # Try square first
            side = px_per_frame ** 0.5
            if abs(side - round(side)) < 1e-6:
                side = int(round(side))
                best = (n_frames, side, side, channels)
                break
            # Try common non-square sizes
            for h in range(8, 300):
                if px_per_frame % h == 0:
                    w = px_per_frame // h
                    if 8 <= w <= 300:
                        best = (n_frames, h, w, channels)
                        break
            if best:
                break
        if best:
            break

    if best is None:
        # Absolute fallback: 1 frame, grayscale, resize to n_features pixels
        side = int(n_features ** 0.5) + 1
        best = (1, side, side, 1)

    n_frames, h, w, channels = best

    # ── Sample frames ────────────────────────────────────────────────────────
    indices = np.linspace(0, total_frames - 1, n_frames, dtype=int)
    parts = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((h, w, 3), dtype=np.uint8)
        if channels == 1:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.resize(frame, (w, h))
            parts.append(frame.flatten())
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (w, h))
            parts.append(frame.flatten())
    cap.release()

    vector = np.concatenate(parts).astype("float32") / 255.0

    # Safety: trim or pad to exactly n_features
    if len(vector) > n_features:
        vector = vector[:n_features]
    elif len(vector) < n_features:
        vector = np.pad(vector, (0, n_features - len(vector)))

    return vector.reshape(1, -1)


CLASS_NAMES = ["healthy", "diseased"]


def predict_image(image_bytes: bytes) -> dict:
    model      = _load_keras()
    tensor     = _preprocess_image_bytes(image_bytes)
    raw_output = model.predict(tensor)

    if raw_output.shape[-1] == 1:
        confidence = float(raw_output[0][0])
        predicted  = "diseased" if confidence >= 0.5 else "healthy"
        confidence = confidence if predicted == "diseased" else 1 - confidence
    else:
        idx        = int(np.argmax(raw_output[0]))
        raw_label  = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else idx
        predicted  = normalise_label(raw_label)
        confidence = float(raw_output[0][idx])

    return {"prediction": predicted, "confidence": round(confidence, 4)}


def predict_video(video_path: str) -> dict:
    model      = _load_sklearn()

    # Read expected feature count directly from the trained model
    n_features = getattr(model, "n_features_in_", 16488)

    features   = _extract_video_feature_vector(video_path, n_features)
    raw        = model.predict(features)[0]
    predicted  = normalise_label(raw)
    proba      = model.predict_proba(features)[0] if hasattr(model, "predict_proba") else None
    confidence = float(max(proba)) if proba is not None else 1.0

    return {
        "prediction": predicted,
        "confidence": round(confidence, 4),
    }


# ── Label normalisation ───────────────────────────────────────────────────────
# The SVM was trained with numeric labels (0 = healthy, 1 = diseased).
# Map any numeric or string variant to the canonical strings used by uploads.py.

_LABEL_MAP = {
    "0": "healthy", "1": "diseased",
    0:   "healthy", 1:   "diseased",
    "healthy": "healthy", "diseased": "diseased",
}

def normalise_label(raw) -> str:
    """Convert model output (0/1 or string) to 'healthy' or 'diseased'."""
    return _LABEL_MAP.get(raw, str(raw))
>>>>>>> 9364d7a7519e50552f01048e76260558573712c4
