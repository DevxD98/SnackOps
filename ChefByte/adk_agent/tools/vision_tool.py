"""
ADK Vision Tool - Extract ingredients from images using Gemini Vision
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from google.adk.tools import FunctionTool
from gemini_setup import get_vision_model
from PIL import Image
import json
from typing import Dict, Any


def extract_ingredients_from_image(image_path: str, image_type: str = "fridge") -> Dict[str, Any]:
    """
    Extract ingredients from images (fridge photos, pantry photos, or grocery receipts).
    Returns a structured list of detected ingredients with quantities and conditions.
    
    Use this tool when:
    - User uploads a photo of their fridge or pantry
    - User shares a grocery receipt image
    - Need to identify ingredients from visual input
    
    Args:
        image_path: Path to the image file
        image_type: Type of image - "fridge", "pantry", or "receipt"
    
    Returns:
        Dictionary containing ingredients list, confidence score, and summary
    """
    try:
        # Load the image
        img = Image.open(image_path)
        
        # Get Gemini Vision model
        model = get_vision_model()
        
        # Create appropriate prompt based on image type
        if image_type == "receipt":
            prompt = _get_receipt_prompt()
        else:
            prompt = _get_fridge_prompt()
        
        # Generate response using Gemini Vision
        response = model.generate_content([prompt, img])
        
        # Parse the response
        result = _parse_response(response.text)
        
        return {
            "success": True,
            "ingredients": result.get("ingredients", []),
            "confidence": result.get("confidence", "medium"),
            "summary": result.get("summary", ""),
            "image_type": image_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ingredients": []
        }


def _get_fridge_prompt() -> str:
    """Get prompt for fridge/pantry analysis"""
    return """
You are analyzing a photo of a refrigerator or pantry. 
Identify ALL visible food items and ingredients with precision.

For each item, extract:
1. Ingredient name (use common English names)
2. Approximate quantity (if visible or estimatable)
3. Condition (fresh, good, wilted, expired, etc.)
4. Confidence level (high, medium, low)

Special considerations for Indian ingredients:
- Identify spices, dals, flours correctly
- Recognize Indian vegetables (karela, bhindi, turai, etc.)
- Identify Indian dairy products (paneer, dahi, etc.)

Return ONLY a JSON object with this format:
{
    "ingredients": [
        {
            "name": "ingredient_name",
            "quantity": "approximate_amount",
            "condition": "fresh/good/wilted/etc",
            "confidence": "high/medium/low"
        }
    ],
    "confidence": "overall_confidence_level",
    "summary": "brief_text_summary"
}

Be thorough but accurate. If unsure about an item, mark confidence as low.
"""


def _get_receipt_prompt() -> str:
    """Get prompt for receipt OCR and parsing"""
    return """
You are analyzing a grocery receipt image.
Extract ALL purchased items with their quantities and prices.

For each item, extract:
1. Item name
2. Quantity (number and unit)
3. Price (if visible)

Normalize ingredient names to standard English terms.
Handle Indian ingredient names (both Hindi and English).

Return ONLY a JSON object with this format:
{
    "ingredients": [
        {
            "name": "ingredient_name",
            "quantity": "amount with unit",
            "price": "price_if_available",
            "confidence": "high/medium/low"
        }
    ],
    "total_amount": "total_price_if_visible",
    "confidence": "overall_confidence_level",
    "summary": "brief_summary_of_purchase"
}

Be precise with quantities and units (kg, grams, liters, pieces, etc.).
"""


def _parse_response(response_text: str) -> Dict[str, Any]:
    """
    Parse Gemini's response to extract structured data
    
    Args:
        response_text: Raw response from Gemini
    
    Returns:
        Parsed dictionary with ingredients and metadata
    """
    try:
        # Try to extract JSON from response
        # Gemini sometimes wraps JSON in markdown code blocks
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text.strip()
        
        # Parse JSON
        result = json.loads(json_str)
        return result
        
    except json.JSONDecodeError as e:
        print(f"⚠ Failed to parse JSON: {e}")
        print(f"Raw response: {response_text[:200]}")
        
        # Fallback: return raw text
        return {
            "ingredients": [],
            "confidence": "low",
            "summary": response_text[:500],
            "parse_error": str(e)
        }


# Create ADK FunctionTool wrapper
vision_tool = FunctionTool(extract_ingredients_from_image)
