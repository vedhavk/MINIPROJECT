from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import io
from PIL import Image

app = FastAPI()

# Load your model (ensure the path matches where you put the file)
model = YOLO("yolov8n-cls.pt") 

@app.get("/")
def read_root():
    return {"status": "Backend is running!"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1. Read the uploaded image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # 2. Run inference
    results = model(image)

    # 3. Extract the top prediction
    # For classification, results[0].probs contains the probabilities
    names_dict = results[0].names
    probs = results[0].probs.data.tolist()
    top_class_idx = results[0].probs.top1
    
    return {
        "prediction": names_dict[top_class_idx],
        "confidence": float(probs[top_class_idx])
    }