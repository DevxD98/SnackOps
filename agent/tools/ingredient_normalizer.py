"""
Ingredient Normalizer - Standardizes ingredient names for consistent matching
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gemini_setup import get_gemini_model
import re


def normalize_ingredients(ingredients):
    """
    Normalize ingredient names to standard forms
    
    Args:
        ingredients: List of ingredient dictionaries or strings
    
    Returns:
        List of normalized ingredient names
    """
    # Extract ingredient names
    ingredient_names = []
    for ing in ingredients:
        if isinstance(ing, dict):
            ingredient_names.append(ing.get('name', ''))
        else:
            ingredient_names.append(str(ing))
    
    # Use Gemini for intelligent normalization
    normalized = _normalize_with_gemini(ingredient_names)
    
    print(f"✓ Normalized {len(normalized)} ingredients")
    return normalized


def _normalize_with_gemini(ingredient_names):
    """
    Use Gemini to normalize ingredient names intelligently
    
    Args:
        ingredient_names: List of raw ingredient names
    
    Returns:
        List of normalized ingredient names
    """
    try:
        model = get_gemini_model("gemini-pro")
        
        # Create prompt for normalization
        prompt = f"""
You are a food ingredient normalizer. Convert these ingredient names to standardized forms.

RULES:
1. Remove quantities (2 lbs, 1 cup, etc.)
2. Remove conditions (fresh, frozen, organic, etc.)
3. Standardize plurals (tomatos → tomatoes, but keep rice as rice)
4. Use common names (roma tomatoes → tomatoes)
5. Fix spelling errors
6. Convert to lowercase
7. Remove brand names
8. Simplify compound names to base ingredient

INGREDIENTS:
{', '.join(ingredient_names)}

Return ONLY a comma-separated list of normalized ingredients, nothing else.

Example input: "2 lbs organic chicken breasts, fresh tomatos, 1 cup of rice, cheddar cheese"
Example output: chicken, tomatoes, rice, cheese
        """
        
        response = model.generate_content(prompt)
        normalized_text = response.text.strip()
        
        # Parse the response
        normalized = [item.strip() for item in normalized_text.split(',')]
        
        # Fallback to rule-based if parsing fails
        if len(normalized) < len(ingredient_names) / 2:
            print("⚠ Gemini normalization incomplete, using fallback...")
            return _rule_based_normalize(ingredient_names)
        
        return normalized
        
    except Exception as e:
        print(f"⚠ Error with Gemini normalization: {str(e)}")
        return _rule_based_normalize(ingredient_names)


def _rule_based_normalize(ingredient_names):
    """
    Fallback rule-based normalization
    
    Args:
        ingredient_names: List of ingredient names
    
    Returns:
        List of normalized names
    """
    normalized = []
    
    # Common replacements
    replacements = {
        'tomatos': 'tomatoes',
        'potatos': 'potatoes',
        'onions': 'onion',
        'carrots': 'carrot',
        'chickens': 'chicken',
        'beefs': 'beef',
        'porks': 'pork'
    }
    
    for name in ingredient_names:
        # Convert to lowercase
        normalized_name = name.lower()
        
        # Remove common descriptors
        descriptors = [
            'organic', 'fresh', 'frozen', 'raw', 'cooked', 'whole', 'sliced',
            'diced', 'chopped', 'minced', 'ground', 'shredded', 'grated',
            'canned', 'dried', 'smoked', 'lean', 'boneless', 'skinless'
        ]
        
        for descriptor in descriptors:
            normalized_name = normalized_name.replace(descriptor, '')
        
        # Remove quantities (numbers + units)
        normalized_name = re.sub(r'\d+\.?\d*\s*(lb|lbs|oz|g|kg|cup|cups|tbsp|tsp|ml|l|gallon|quart|pint)', '', normalized_name)
        normalized_name = re.sub(r'\d+\.?\d*', '', normalized_name)
        
        # Remove extra whitespace
        normalized_name = ' '.join(normalized_name.split())
        
        # Apply common replacements
        for old, new in replacements.items():
            if old in normalized_name:
                normalized_name = normalized_name.replace(old, new)
        
        # Get the core ingredient (first significant word or two)
        words = normalized_name.split()
        if words:
            # Take last 1-2 words as the ingredient
            if len(words) >= 2:
                normalized_name = ' '.join(words[-2:])
            else:
                normalized_name = words[-1]
        
        if normalized_name.strip():
            normalized.append(normalized_name.strip())
    
    return normalized


def remove_duplicates(ingredients):
    """
    Remove duplicate ingredients
    
    Args:
        ingredients: List of ingredient names
    
    Returns:
        List with duplicates removed
    """
    return list(set(ingredients))


def categorize_ingredients(ingredients):
    """
    Categorize ingredients by type
    
    Args:
        ingredients: List of ingredient names
    
    Returns:
        Dictionary of categorized ingredients
    """
    categories = {
        'proteins': [],
        'vegetables': [],
        'fruits': [],
        'grains': [],
        'dairy': [],
        'other': []
    }
    
    # Simple keyword matching (in production, use Gemini for better accuracy)
    for ing in ingredients:
        ing_lower = ing.lower()
        
        if any(protein in ing_lower for protein in ['chicken', 'beef', 'pork', 'fish', 'tofu', 'egg', 'turkey', 'lamb']):
            categories['proteins'].append(ing)
        elif any(veg in ing_lower for veg in ['tomato', 'lettuce', 'carrot', 'broccoli', 'pepper', 'onion', 'celery', 'spinach']):
            categories['vegetables'].append(ing)
        elif any(fruit in ing_lower for fruit in ['apple', 'banana', 'orange', 'berry', 'grape', 'melon', 'peach']):
            categories['fruits'].append(ing)
        elif any(grain in ing_lower for grain in ['rice', 'pasta', 'bread', 'flour', 'oat', 'quinoa', 'barley']):
            categories['grains'].append(ing)
        elif any(dairy in ing_lower for dairy in ['milk', 'cheese', 'yogurt', 'butter', 'cream']):
            categories['dairy'].append(ing)
        else:
            categories['other'].append(ing)
    
    return categories


# Example usage
if __name__ == "__main__":
    # Test normalization
    test_ingredients = [
        {"name": "2 lbs organic chicken breasts", "quantity": "2 lbs"},
        {"name": "fresh tomatos", "quantity": "5"},
        {"name": "1 cup basmati rice", "quantity": "1 cup"},
        "cheddar cheese block",
        "baby carrots",
        "frozen peas"
    ]
    
    print("Original Ingredients:")
    print("="*50)
    for ing in test_ingredients:
        if isinstance(ing, dict):
            print(f"• {ing['name']}")
        else:
            print(f"• {ing}")
    
    normalized = normalize_ingredients(test_ingredients)
    
    print("\n\nNormalized Ingredients:")
    print("="*50)
    for ing in normalized:
        print(f"• {ing}")
    
    print("\n\nCategorized:")
    print("="*50)
    categorized = categorize_ingredients(normalized)
    for category, items in categorized.items():
        if items:
            print(f"{category.upper()}: {', '.join(items)}")
