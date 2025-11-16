"""
Vision Tool - Uses Gemini Vision to extract ingredients from fridge photos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gemini_setup import get_vision_model
from PIL import Image
import json


def extract_ingredients_from_image(image_path):
    """
    Use Gemini Vision to identify ingredients from a fridge photo
    
    Args:
        image_path: Path to the image file
    
    Returns:
        List of ingredients detected in the image
    """
    try:
        # Load the image
        img = Image.open(image_path)
        
        # Get Gemini Vision model
        model = get_vision_model()
        
        # Create prompt for ingredient extraction
        prompt = """
You are analyzing a photo of a refrigerator or pantry. 
Identify ALL visible food items and ingredients.

For each item, list:
1. The ingredient name
2. Approximate quantity (if visible)
3. Condition (fresh, wilted, etc.)

Return ONLY a JSON array of objects with this format:
[
    {"name": "ingredient_name", "quantity": "approximate_amount", "condition": "fresh/good/wilted/etc"},
    ...
]

Be specific but concise. Include items like:
- Vegetables and fruits
- Dairy products
- Meats and proteins
- Condiments and sauces
- Beverages
- Packaged foods

Example output:
[
    {"name": "tomatoes", "quantity": "4-5", "condition": "fresh"},
    {"name": "milk", "quantity": "1 carton", "condition": "good"},
    {"name": "chicken breast", "quantity": "2 pieces", "condition": "fresh"}
]
        """
        
        # Generate response
        response = model.generate_content([prompt, img])
        
        # Parse response
        ingredients = _parse_ingredient_response(response.text)
        
        print(f"✓ Extracted {len(ingredients)} ingredients from image")
        return ingredients
        
    except Exception as e:
        print(f"✗ Error extracting ingredients: {str(e)}")
        return []


def _parse_ingredient_response(response_text):
    """
    Parse the Gemini Vision response to extract ingredient list
    
    Args:
        response_text: Raw text response from Gemini
    
    Returns:
        List of ingredient dictionaries
    """
    try:
        # Try to extract JSON from response
        # Remove markdown code blocks if present
        clean_text = response_text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
        
        # Parse JSON
        ingredients = json.loads(clean_text.strip())
        
        return ingredients
        
    except json.JSONDecodeError:
        # Fallback: try to parse as simple list
        print("⚠ Could not parse JSON, attempting text parsing...")
        return _fallback_parse(response_text)


def _fallback_parse(text):
    """
    Fallback parser for non-JSON responses
    
    Args:
        text: Raw response text
    
    Returns:
        List of ingredient dictionaries
    """
    ingredients = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('*'):
            # Simple extraction - assume format "ingredient - quantity"
            parts = line.split('-')
            if len(parts) >= 1:
                name = parts[0].strip().strip('•').strip('*').strip('1234567890.)')
                quantity = parts[1].strip() if len(parts) > 1 else "unknown"
                
                if name:
                    ingredients.append({
                        "name": name,
                        "quantity": quantity,
                        "condition": "unknown"
                    })
    
    return ingredients


# Example usage
if __name__ == "__main__":
    # Test with a sample image
    ingredients = extract_ingredients_from_image("sample_fridge.jpg")
    
    print("\nExtracted Ingredients:")
    print("="*50)
    for ing in ingredients:
        print(f"• {ing['name']} ({ing['quantity']}) - {ing['condition']}")
