import os
import sys
import cv2
import numpy as np
import joblib

MODEL_PATH = "duck_disease_model.pkl"


def extract_features(video_path):
    cap = cv2.VideoCapture(video_path)

    ret, prev = cap.read()
    if not ret:
        cap.release()
        return None

    prev = cv2.resize(prev, (320, 240))
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    motion_magnitudes = []
    motion_directions = []

    frame_count = 0
    skip = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % skip != 0:
            continue

        frame = cv2.resize(frame, (320, 240))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(
            prev_gray,
            gray,
            None,
            0.5,
            2,
            10,
            2,
            3,
            1.1,
            0,
        )

        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        motion_magnitudes.append(np.mean(magnitude))
        motion_directions.append(np.std(angle))

        prev_gray = gray

    cap.release()

    if len(motion_magnitudes) == 0:
        return None

    return [
        np.mean(motion_magnitudes),
        np.std(motion_magnitudes),
        np.mean(motion_directions),
        np.std(motion_directions),
    ]


def load_model(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


def predict(video_path, model):
    features = extract_features(video_path)
    if features is None:
        raise ValueError("Unable to extract features from video.")

    features = np.array(features).reshape(1, -1)
    pred = model.predict(features)
    return "Diseased Duck" if pred[0] == 1 else "Healthy Duck"


def main():
    if len(sys.argv) != 2:
        print("Usage: python predict_duck_disease.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        sys.exit(1)

    model = load_model(MODEL_PATH)
    result = predict(video_path, model)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()

# "D:\Dowloads\176939-856259165_medium (1).mp4"