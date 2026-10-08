import io
import os

import mlflow
import numpy as np
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from torchvision import transforms

# Overridable from inside a container (docker run -e MLFLOW_TRACKING_URI=...)
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Loaded once at startup, through the registry alias (not a .pth file)
model = mlflow.pyfunc.load_model("models:/food11@champion")

# Must be in sorted order = the label order ImageFolder used during training.
# Replace with the output of: Get-ChildItem data\food11_processed_mini\training -Name
CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

# Same preprocessing as training: 128x128 (done by data.py), ToTensor, ImageNet normalisation
TRANSFORM = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    batch = TRANSFORM(image).unsqueeze(0).numpy()  # shape (1, 3, 128, 128), float32

    logits = np.asarray(model.predict(batch))[0]
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()  # softmax
    idx = int(probs.argmax())

    return {"category": CLASSES[idx], "confidence": float(probs[idx])}