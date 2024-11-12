from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
from tensorflow.keras.applications.resnet_v2 import preprocess_input
import os
import uvicorn
import logging
import gdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Set paths and Google Drive file ID
MODEL_PATH = "WeatherModel.keras"
GOOGLE_DRIVE_FILE_ID = "1bZjPgcYfrBVUXuYu9lTSwzL1byiILuJH"

# Define class labels
class_labels = [
    "dew", "fogsmog", "frost", "glaze", "hail",
    "lightning", "rain", "rainbow", "rime",
    "sandstorm", "snow"
]

model = None

def download_from_drive():
    try:
        logger.info("Attempting to download model...")
        
        url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"
        
        output = gdown.download(url, MODEL_PATH, quiet=False)
        
        if output is None:
            logger.error("Download failed")
            return False
            
        logger.info("Model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False

def load_model_safe():
    try:
        global model
        if model is None:
            logger.info("Loading model...")
            if not os.path.exists(MODEL_PATH):
                success = download_from_drive()
                if not success:
                    return False
            model = load_model(MODEL_PATH)
            logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    if not load_model_safe():
        logger.error("Failed to initialize model during startup")
    else:
        logger.info("Model initialized successfully during startup")

# Set up CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading index.html: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading page")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Ensure model is loaded
        if model is None and not load_model_safe():
            raise HTTPException(status_code=500, detail="Model not available")

        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        image = image.resize((256, 256))
        image_array = np.expand_dims(np.array(image), axis=0)
        image_array = preprocess_input(image_array)

        # Make prediction
        predictions = model.predict(image_array)[0]
        top_indices = np.argsort(predictions)[-3:][::-1]

        # Structure response
        result = {
            "predicted_class": class_labels[top_indices[0]],
            "prediction": float(predictions[top_indices[0]]),
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

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing image")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)