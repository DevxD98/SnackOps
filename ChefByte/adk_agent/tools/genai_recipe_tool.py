"""
ADK GenAI Recipe Tool - Generate creative recipes using Gemini (FunctionTool)
"""
import os
import sys
import json
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from google.adk.tools import FunctionTool

def generate_recipe(
    ingredients: List[str],
    dietary_constraints: Optional[List[str]] = None,
    cuisine_type: Optional[str] = None,
    meal_type: Optional[str] = None,
    cooking_time: Optional[str] = "30 minutes"
) -> Dict[str, Any]:
    """
    Generates a custom recipe based on available ingredients using GenAI.
    
    Use this tool when:
    - The user wants a creative or custom recipe.
    - The database search returns no good matches.
    - The user has a weird combination of ingredients.
    
    Args:
        ingredients: List of available ingredients.
        dietary_constraints: List of dietary needs (e.g., vegetarian, vegan).
        cuisine_type: Preferred cuisine (e.g., Indian, Italian).
        meal_type: Type of meal (e.g., Breakfast, Dinner, Snack).
        cooking_time: Preferred max cooking time.
        
    Returns:
        Dictionary containing the generated recipe details.
    """
    try:
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {"success": False, "error": "API Key not found"}
            
        genai.configure(api_key=api_key)
        model_id = "gemini-2.5-flash"
        model = genai.GenerativeModel(model_id)
        
        prompt = f"""
        You are a master chef. Create a delicious recipe using these ingredients: {', '.join(ingredients)}.
        
        Constraints:
        - Diet: {', '.join(dietary_constraints) if dietary_constraints else 'None'}
        - Cuisine: {cuisine_type if cuisine_type else 'Any'}
        - Meal Type: {meal_type if meal_type else 'Any'}
        - Time: {cooking_time}
        
        The recipe MUST use the provided ingredients as the main stars, but you can assume basic pantry staples (oil, salt, spices, water) are available.
        
        Return ONLY valid JSON with this structure:
        {{
            "name": "Recipe Name",
            "description": "A mouth-watering description",
            "cuisine": "Cuisine Type",
            "prep_time": "XX minutes",
            "calories": 500,
            "protein_g": 20,
            "carbs_g": 30,
            "fat_g": 15,
            "ingredients": ["List", "of", "ingredients", "with", "quantities"],
            "instructions": ["Step 1 description", "Step 2 description", "Step 3 description"],
            "match_score": 95
        }}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            raw_text = response.text
            print(f"🤖 GenAI Raw Response: {raw_text[:200]}...") # Log first 200 chars
            
            # Clean up markdown code blocks if present
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].strip()
                
            try:
                recipe_data = json.loads(raw_text)
                return {
                    "success": True,
                    "recipe": recipe_data,
                    "source": "genai"
                }
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"❌ Failed Text: {raw_text}")
                return {"success": False, "error": f"JSON Parse Error: {e}"}
        else:
             print("❌ No response text from Gemini")
             return {"success": False, "error": "No response from model"}

    except Exception as e:
        print(f"❌ GenAI Tool Error: {e}")
        return {"success": False, "error": str(e)}

# Create ADK FunctionTool wrapper
genai_recipe_tool = FunctionTool(generate_recipe)
