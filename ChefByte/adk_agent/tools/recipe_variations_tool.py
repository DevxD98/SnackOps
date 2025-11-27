"""
ADK Recipe Variations Tool - Generate 3 recipe variations in one call
"""
import os
import json
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from google.adk.tools import FunctionTool

def generate_recipe_variations(
    ingredients: List[str],
    dietary_constraints: Optional[List[str]] = None,
    cuisine_type: Optional[str] = None,
    cooking_time: Optional[str] = "30 minutes",
    servings: int = 2
) -> Dict[str, Any]:
    """
    Generates 3 recipe variations in a single call for performance.
    
    This is optimized for agentic workflows where the agent needs multiple
    recipe options quickly.
    
    Args:
        ingredients: List of available ingredients.
        dietary_constraints: List of dietary needs (e.g., vegetarian, vegan).
        cuisine_type: Preferred cuisine (e.g., Indian, Italian).
        cooking_time: Preferred max cooking time.
        servings: Number of servings.
        
    Returns:
        Dictionary containing 3 recipe variations.
    """
    try:
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {"success": False, "error": "API Key not found"}
            
        genai.configure(api_key=api_key)
        model_id = "gemini-2.5-flash"
        model = genai.GenerativeModel(model_id)
        
        # Craft a prompt that requests 3 variations
        prompt = f"""
        You are a master chef. Create 3 DIFFERENT recipe variations using these ingredients: {', '.join(ingredients)}.
        
        Constraints:
        - Diet: {', '.join(dietary_constraints) if dietary_constraints else 'None'}
        - Cuisine: {cuisine_type if cuisine_type else 'Any'}
        - Time: {cooking_time}
        - Servings: {servings}
        
        The recipes MUST use the provided ingredients as the main components, but you can assume basic pantry staples (oil, salt, spices, water) are available.
        
        Create 3 variations:
        1. **Standard**: A classic, well-balanced recipe
        2. **Creative Twist**: An innovative fusion or unexpected combination
        3. **Quick & Easy**: A simplified, time-saving version
        
        Return ONLY valid JSON with this EXACT structure:
        {{
            "variations": [
                {{
                    "name": "Recipe Name",
                    "description": "A mouth-watering description",
                    "cuisine": "Cuisine Type",
                    "prep_time": "XX minutes",
                    "calories": 500,
                    "protein_g": 20,
                    "carbs_g": 30,
                    "fat_g": 15,
                    "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity"],
                    "instructions": ["Step 1 description", "Step 2 description"],
                    "match_score": 95,
                    "variation_type": "Standard"
                }},
                {{
                    "name": "Recipe Name 2",
                    "description": "Another description",
                    "cuisine": "Cuisine Type",
                    "prep_time": "XX minutes",
                    "calories": 450,
                    "protein_g": 18,
                    "carbs_g": 28,
                    "fat_g": 12,
                    "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity"],
                    "instructions": ["Step 1 description", "Step 2 description"],
                    "match_score": 95,
                    "variation_type": "Creative Twist"
                }},
                {{
                    "name": "Recipe Name 3",
                    "description": "Third description",
                    "cuisine": "Cuisine Type",
                    "prep_time": "XX minutes",
                    "calories": 400,
                    "protein_g": 15,
                    "carbs_g": 25,
                    "fat_g": 10,
                    "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity"],
                    "instructions": ["Step 1 description", "Step 2 description"],
                    "match_score": 95,
                    "variation_type": "Quick & Easy"
                }}
            ]
        }}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.8  # Higher creativity for variations
            )
        )
        
        if response.text:
            raw_text = response.text
            print(f"🤖 GenAI Variations Response: {raw_text[:200]}...")
            
            # Clean up markdown code blocks if present
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].strip()
                
            try:
                data = json.loads(raw_text)
                recipes = data.get('variations', [])
                
                # Ensure we have 3 recipes
                if len(recipes) < 3:
                    print(f"⚠️ Only got {len(recipes)} recipes, expected 3")
                
                return {
                    "success": True,
                    "recipes": recipes,
                    "source": "genai_variations"
                }
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"❌ Failed Text: {raw_text}")
                return {"success": False, "error": f"JSON Parse Error: {e}"}
        else:
             print("❌ No response text from Gemini")
             return {"success": False, "error": "No response from model"}

    except Exception as e:
        print(f"❌ Recipe Variations Tool Error: {e}")
        return {"success": False, "error": str(e)}

# Create ADK FunctionTool wrapper
recipe_variations_tool = FunctionTool(generate_recipe_variations)
