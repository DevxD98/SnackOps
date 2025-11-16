"""
Centralized Gemini API configuration
Import this module in all tools that need Gemini access
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_model(model_name="gemini-pro"):
    """
    Get a Gemini model instance
    
    Args:
        model_name: Name of the model ('gemini-pro' or 'gemini-pro-vision')
    
    Returns:
        GenerativeModel instance
    """
    return genai.GenerativeModel(model_name)

def get_vision_model():
    """Get Gemini Vision model"""
    return genai.GenerativeModel('gemini-pro-vision')
