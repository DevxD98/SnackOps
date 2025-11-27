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
        
        # Create a unified prompt that handles both cases
        prompt = _get_unified_prompt()
        
        # Generate response using Gemini Vision
        response = model.generate_content([prompt, img])
        
        # Parse the response
        result = _parse_response(response.text)
        
        # Determine image type from result if possible
        detected_type = result.get("detected_type", image_type)
        
        return {
            "success": True,
            "ingredients": result.get("ingredients", []),
            "confidence": result.get("confidence", "medium"),
            "summary": result.get("summary", ""),
            "image_type": detected_type,
            "receipt_data": {
                "storeName": result.get("store_name"),
                "date": result.get("date"),
                "total": result.get("total_amount")
            } if detected_type == "receipt" else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ingredients": []
        }


def _get_unified_prompt() -> str:
    """Get a unified prompt that can handle both fridge photos and receipts"""
    return """
You are an advanced AI food analyzer. Analyze the provided image, which could be either a **Fridge/Pantry Photo** OR a **Grocery Receipt**.

First, determine the image type.

### IF IT IS A RECEIPT:
Extract the following details:
1. **Store Name**: The name of the store/merchant.
2. **Date**: The date of purchase (YYYY-MM-DD format if possible).
3. **Total Amount**: The final total price paid.
4. **Items**: List of all purchased items.
   - Name: Normalize to standard English ingredient names.
   - Quantity: Amount/weight if visible.
   - Price: Price of the item.

### IF IT IS A FRIDGE/PANTRY PHOTO:
Identify ALL visible food items/ingredients.
1. **Ingredients**: List of all items.
   - Name: Standard English name (handle Indian ingredients like 'bhindi', 'paneer' correctly).
   - Quantity: Approximate amount visible.
   - Condition: Fresh, good, etc.

### RETURN FORMAT (JSON ONLY):
{
    "detected_type": "receipt" OR "fridge",
    "store_name": "Store Name (if receipt)",
    "date": "Date (if receipt)",
    "total_amount": "Total (if receipt)",
    "ingredients": [
        {
            "name": "Item Name",
            "quantity": "Qty",
            "price": "Price (if receipt)",
            "condition": "Condition (if fridge)",
            "confidence": "high/medium/low"
        }
    ],
    "confidence": "overall_confidence",
    "summary": "Brief summary of what was detected"
}

Be precise and thorough. If it's a receipt, the 'ingredients' list should contain the purchased items.
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
