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

def get_gemini_model(model_name="gemini-2.5-flash"):
    """
    Get a Gemini model instance
    
    Args:
        model_name: Name of the model (default: 'gemini-2.5-flash')
        Other options: 'gemini-2.5-pro', 'gemini-2.0-flash-exp'
    
    Returns:
        GenerativeModel instance
    """
    return genai.GenerativeModel(model_name)

def get_vision_model():
    """Get Gemini model with vision capabilities (2.5-flash supports vision)"""
    return genai.GenerativeModel('gemini-2.5-flash')
