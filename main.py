from fastapi import FastAPI, File, UploadFile
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
from tensorflow.keras.applications.resnet_v2 import preprocess_input
import os
import uvicorn

app = FastAPI()

# Load your model and specify class labels
model_path = r"WeatherModel.keras"  # Update with your actual path
model = load_model(model_path)
class_labels = [
    "dew", "fogsmog", "frost", "glaze", "hail",
    "lightning", "rain", "rainbow", "rime",
    "sandstorm", "snow"
]

# Set up CORS to allow requests from any origin
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image and preprocess
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')
    image = image.resize((256, 256))  # Ensure target size matches model input
    image_array = np.expand_dims(np.array(image), axis=0)
    image_array = preprocess_input(image_array)

    # Make prediction
    predictions = model.predict(image_array)[0]
    top_indices = np.argsort(predictions)[-3:][::-1]

    # Structure response with top 3 predictions
    result = {
        "predicted_class": class_labels[top_indices[0]],
        "confidence": float(predictions[top_indices[0]] * 100),
        "top_predictions": [
            {
                "class": class_labels[idx],
                "probability": float(predictions[idx]),
                "percentage": float(predictions[idx] * 100)
            }
            for idx in top_indices
        ]
    }
    return result

@app.get("/")
async def root():
    return {"message": "Weather Image Prediction API"}

# Run the server using uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
