from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
from dotenv import load_dotenv
from tensorflow.keras.applications.resnet_v2 import preprocess_input
import os
import uvicorn
import logging
import gdown
from firebase_config import FirebaseManager
import dropbox
from dropbox.exceptions import ApiError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
load_dotenv()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set paths and Google Drive file ID
MODEL_PATH = "WeatherModel.keras"
GOOGLE_DRIVE_FILE_ID = "1bZjPgcYfrBVUXuYu9lTSwzL1byiILuJH"

DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
dropbox_client = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Define class labels
class_labels = [
    "dew", "fogsmog", "frost", "glaze", "hail",
    "lightning", "rain", "rainbow", "rime",
    "sandstorm", "snow"
]

# Declare global variables
global model, firebase_manager
model = None
firebase_manager = None

def download_from_drive():
    """Download the model file from Google Drive if it doesn't exist"""
    try:
        if not os.path.exists(MODEL_PATH):
            logger.info("Downloading model from Google Drive...")
            gdown.download(f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}", MODEL_PATH, quiet=False)
            logger.info("Model downloaded successfully")
            return True
        return True
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False


def upload_to_dropbox(file_data, file_name, unique_key):
    """
    Uploads a file to Dropbox and associates it with the unique key.
    """
    try:
        # Define the Dropbox path (e.g., "/uploads/unique_key_filename.ext")
        dropbox_path = f"/uploads/{unique_key}_{file_name}"
        
        # Upload the file
        dropbox_client.files_upload(file_data, dropbox_path)
        return dropbox_path  # Return the file path for further use
    except ApiError as e:
        logger.error(f"Dropbox upload error: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file to Dropbox")



def load_model_safe():
    """Safely load the model into memory"""
    global model
    try:
        if model is None:
            if not os.path.exists(MODEL_PATH):
                if not download_from_drive():
                    return False
            logger.info("Loading model...")
            model = load_model(MODEL_PATH)
            logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize both model and Firebase during startup"""
    global model, firebase_manager
    try:
        # Load the model
        if not load_model_safe():
            logger.error("Failed to initialize model during startup")
            raise Exception("Model initialization failed")
        
        # Initialize Firebase
        firebase_manager = FirebaseManager()
        logger.info("Startup completed successfully - Model and Firebase initialized")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't raise the exception here - let the application start anyway
        # Individual endpoints will handle the unavailability of model/firebase

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    global model, firebase_manager
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Read and preprocess the image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        image = image.resize((256, 256))
        image_array = np.array(image).astype(np.float32)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = preprocess_input(image_array)
        
        # Get predictions
        predictions = model.predict(image_array)[0]
        top_indices = np.argsort(predictions)[-3:][::-1]
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

        # Save to Firebase and Dropbox
        unique_key = None
        dropbox_path = None

        if firebase_manager:
            try:
                # Save prediction to Firebase and get unique key
                unique_key = firebase_manager.save_prediction(result, file.filename)
                logger.info(f"Prediction saved to Firebase with ID: {unique_key}")

                # Upload the file to Dropbox with unique key
                dropbox_path = upload_to_dropbox(contents, file.filename, unique_key)
                logger.info(f"File uploaded to Dropbox at {dropbox_path}")
            except Exception as e:
                logger.error(f"Error saving to Firebase or Dropbox: {str(e)}")
        
        # Add paths and keys to response
        result.update({
            "prediction_id": unique_key,
            "dropbox_path": dropbox_path
        })

        return result

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recent-predictions")
async def get_recent_predictions():
    try:
        if not firebase_manager:
            return {"predictions": []}  # Return empty list if Firebase is not initialized
        
        predictions = firebase_manager.get_recent_predictions()
        return {"predictions": predictions}
        
    except Exception as e:
        logger.error(f"Error retrieving predictions: {str(e)}")
        return {"predictions": []}  # Return empty list on error

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML file for the application."""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("The index.html file was not found in the static directory.")
        raise HTTPException(status_code=404, detail="Page not found")
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        raise HTTPException(status_code=500, detail="Error serving page")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)