from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
from tensorflow.keras.applications.resnet_v2 import preprocess_input
import os
import uvicorn
import gdown

app = FastAPI()

# Set paths and Google Drive file ID
MODEL_PATH = r"./WeatherModel.keras"  # Local path where the model will be stored
GOOGLE_DRIVE_FILE_ID = "1bZjPgcYfrBVUXuYu9lTSwzL1byiILuJH"

# Define class labels
class_labels = [
    "dew", "fogsmog", "frost", "glaze", "hail",
    "lightning", "rain", "rainbow", "rime",
    "sandstorm", "snow"
]

# Function to download model from Google Drive if not already present
def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
    else:
        print("Model already downloaded.")

# Load model at startup
@app.on_event("startup")
async def startup_event():
    download_model()
    global model
    model = load_model(MODEL_PATH)

# Set up CORS to allow requests from any origin
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (like images, stylesheets, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html as the home page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

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

# Run the server using uvicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
