import os
import logging
from typing import Dict, List
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherChatbot:
    def __init__(self):
        try:
            # Configure the API key from environment variable
            genai.configure(api_key='')
            
            # System prompts for different contexts
            self.safety_system_prompt = """
            You are an expert weather safety advisor. Always provide precise, actionable safety guidance 
            for various weather conditions. Prioritize human safety and give clear, concise instructions. 
            Your responses should be informative, calm, and provide step-by-step safety recommendations.
            Keep your responses under 100 words and dont answer unrelated to the weather safety topic.
            """
            
            self.classification_system_prompt = """
            You are a weather classification expert. When given a weather condition, 
            provide detailed, scientific insights about the condition, its characteristics, 
            formation, and potential impacts. Use technical language and provide precise information.
            Keep your responses under 100 words and dont answer unrelated to the weather classification topic.
            """
            
            # Initialize models for different contexts
            self.safety_model = genai.GenerativeModel(
                model_name='gemini-1.5-pro', 
                system_instruction=self.safety_system_prompt
            )
            
            self.classification_model = genai.GenerativeModel(
                model_name='gemini-1.5-pro', 
                system_instruction=self.classification_system_prompt
            )
            
            logger.info("WeatherChatbot initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing WeatherChatbot: {e}")
            raise

    def get_image_classification_insights(self, weather_type: str) -> Dict[str, str]:
        try:
            response = self.classification_model.generate_content(
                f"Provide comprehensive scientific details about {weather_type}. "
                "Include its formation process, typical characteristics, and meteorological significance. Keep your responses under 100 words and dont answer unrelated to the weather classification topic."
            )
            return {
                "scientific_details": response.text,
                "type": weather_type
            }
        except Exception as e:
            logger.error(f"Error in image classification insights: {e}")
            return {
                "scientific_details": "Unable to generate insights at the moment.",
                "type": weather_type
            }

    def get_safety_recommendations(self, weather_type: str) -> Dict[str, str]:
        try:
            response = self.safety_model.generate_content(
                f"Provide detailed safety guidelines for being outdoors or traveling during {weather_type}. "
                "Include precautions, potential risks, and recommended actions. Keep your responses under 100 words and dont answer unrelated to the weather classification topic."
            )
            return {
                "safety_recommendations": response.text,
                "type": weather_type
            }
        except Exception as e:
            logger.error(f"Error in safety recommendations: {e}")
            return {
                "safety_recommendations": "Unable to generate safety recommendations at the moment.",
                "type": weather_type
            }

    def general_weather_query(self, query: str) -> str:
        try:
            response = self.safety_model.generate_content(query)
            return response.text
        except Exception as e:
            logger.error(f"Error in general weather query: {e}")
            return "I apologize, but I couldn't process your query at the moment."
