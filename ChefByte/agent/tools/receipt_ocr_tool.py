"""
Receipt OCR Tool - Extracts items from grocery receipt images
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gemini_setup import get_vision_model
from PIL import Image
import json
import re


def extract_items_from_receipt(receipt_image_path):
    """
    Use Gemini Vision to extract purchased items from a receipt
    
    Args:
        receipt_image_path: Path to the receipt image
    
    Returns:
        List of items with quantities and prices
    """
    try:
        # Load the receipt image
        img = Image.open(receipt_image_path)
        
        # Get Gemini Vision model
        model = get_vision_model()
        
        # Create prompt for receipt parsing
        prompt = """
You are analyzing a grocery receipt. Extract ALL purchased items.

For each item, identify:
1. Product name
2. Quantity (if shown)
3. Price
4. Category (produce, dairy, meat, bakery, etc.)

Return ONLY a JSON array:
[
    {
        "item": "product_name",
        "quantity": "amount",
        "price": "cost",
        "category": "category_name"
    },
    ...
]

Example:
[
    {"item": "organic tomatoes", "quantity": "1.5 lb", "price": "4.99", "category": "produce"},
    {"item": "milk 2%", "quantity": "1 gallon", "price": "3.49", "category": "dairy"},
    {"item": "chicken breast", "quantity": "2 lb", "price": "8.99", "category": "meat"}
]

Focus on food items only. Ignore non-food items, taxes, and totals.
        """
        
        # Generate response
        response = model.generate_content([prompt, img])
        
        # Parse response
        items = _parse_receipt_response(response.text)
        
        print(f"✓ Extracted {len(items)} items from receipt")
        return items
        
    except Exception as e:
        print(f"✗ Error extracting receipt items: {str(e)}")
        return []


def _parse_receipt_response(response_text):
    """
    Parse the Gemini Vision response to extract item list
    
    Args:
        response_text: Raw text response from Gemini
    
    Returns:
        List of item dictionaries
    """
    try:
        # Clean the response
        clean_text = response_text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
        
        # Parse JSON
        items = json.loads(clean_text.strip())
        
        return items
        
    except json.JSONDecodeError:
        print("⚠ Could not parse JSON from receipt, using fallback...")
        return _fallback_receipt_parse(response_text)


def _fallback_receipt_parse(text):
    """
    Fallback parser for receipt text
    
    Args:
        text: Raw response text
    
    Returns:
        List of item dictionaries
    """
    items = []
    lines = text.strip().split('\n')
    
    for line in lines:
        # Look for lines with prices (format: item ... $X.XX)
        if '$' in line or re.search(r'\d+\.\d{2}', line):
            # Simple extraction
            parts = re.split(r'\s{2,}|\$', line)
            if len(parts) >= 2:
                item_name = parts[0].strip().strip('•').strip('*').strip('1234567890.)')
                price_match = re.search(r'(\d+\.\d{2})', line)
                price = price_match.group(1) if price_match else "0.00"
                
                if item_name and len(item_name) > 2:
                    items.append({
                        "item": item_name,
                        "quantity": "1",
                        "price": price,
                        "category": "unknown"
                    })
    
    return items


def convert_to_ingredients(receipt_items):
    """
    Convert receipt items to ingredient format
    
    Args:
        receipt_items: List of items from receipt
    
    Returns:
        List of ingredients in standard format
    """
    ingredients = []
    
    for item in receipt_items:
        ingredients.append({
            "name": item.get("item", ""),
            "quantity": item.get("quantity", "1"),
            "condition": "fresh",
            "source": "receipt"
        })
    
    return ingredients


# Example usage
if __name__ == "__main__":
    # Test with a sample receipt
    items = extract_items_from_receipt("sample_receipt.jpg")
    
    print("\nExtracted Receipt Items:")
    print("="*50)
    for item in items:
        print(f"• {item['item']} - {item['quantity']} - ${item['price']} ({item['category']})")
    
    print("\n\nConverted to Ingredients:")
    print("="*50)
    ingredients = convert_to_ingredients(items)
    for ing in ingredients:
        print(f"• {ing['name']} ({ing['quantity']})")
