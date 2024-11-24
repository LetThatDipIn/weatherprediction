import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

class FirebaseManager:
    def __init__(self):
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.predictions_ref = self.db.collection('weather_predictions')
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            raise

    def save_prediction(self, prediction_data, image_name):
        """
        Save prediction data to Firestore
        """
        try:
            timestamp = datetime.now()
            doc_data = {
                'timestamp': timestamp,
                'image_name': image_name,
                'predicted_class': prediction_data['predicted_class'],
                'confidence': prediction_data['prediction'],
                'top_predictions': prediction_data['top_predictions'],
            }
            
            # Add the document to Firestore
            doc_ref = self.predictions_ref.add(doc_data)
            return doc_ref[1].id  # Return the document ID
            
        except Exception as e:
            print(f"Error saving to Firebase: {str(e)}")
            raise

    def get_recent_predictions(self, limit=10):
        """
        Retrieve recent predictions from Firestore
        """
        try:
            docs = (self.predictions_ref
                   .order_by('timestamp', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            return [{
                'id': doc.id,
                **doc.to_dict()
            } for doc in docs]
            
        except Exception as e:
            print(f"Error retrieving from Firebase: {str(e)}")
            raise

# Modified main.py with Firebase integration:
from fastapi import FastAPI, File, UploadFile, HTTPException
from firebase_config import FirebaseManager
import logging

# Initialize Firebase Manager
firebase_manager = None
