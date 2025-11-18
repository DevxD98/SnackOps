"""
ADK Recipe Search Tool - Find recipes matching available ingredients (FunctionTool)
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from google.adk.tools import FunctionTool
import pandas as pd
from typing import Dict, List, Any, Optional


def search_recipes(
    available_ingredients: List[str],
    dietary_constraints: Optional[List[str]] = None,
    max_missing: int = 2,
    cuisine_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for recipes that match available ingredients and dietary constraints.
    Returns a list of recipes with match scores, missing ingredients, and recipe details.
    
    Use this tool when user has ingredients and needs recipe suggestions, especially for:
    - Finding recipes with available ingredients
    - Filtering by dietary needs (vegetarian, vegan, gluten-free, Jain, halal)
    - Indian cuisine preferences (Punjabi, South Indian, Bengali, etc.)
    
    Args:
        available_ingredients: List of ingredient names you have (e.g., ["tomato", "onion", "rice"])
        dietary_constraints: List of dietary requirements (e.g., ["vegetarian", "gluten_free"])
        max_missing: Maximum number of missing ingredients allowed (default: 2)
        cuisine_type: Cuisine filter like "indian", "punjabi", "south_indian" (optional)
    
    Returns:
        Dictionary with:
        - recipes: List of matching recipes with match scores and nutrition
        - total_found: Total number of matching recipes
        - filters_applied: Summary of applied filters
    """
    try:
        # Get recipes database path
        recipes_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "recipes.csv"
        )
        
        # Load recipes
        recipes_df = _load_recipes(recipes_path)
        
        if recipes_df.empty:
            return {
                "success": False,
                "error": "No recipes found in database",
                "recipes": []
            }
        
        # Apply filters
        filtered_df = recipes_df.copy()
        
        # Filter by dietary constraints
        if dietary_constraints:
            filtered_df = _filter_by_diet(filtered_df, dietary_constraints)
        
        # Filter by cuisine type
        if cuisine_type:
            filtered_df = _filter_by_cuisine(filtered_df, cuisine_type)
        
        # Score recipes by ingredient match
        scored_recipes = _score_recipes(
            filtered_df,
            available_ingredients,
            max_missing
        )
        
        # Sort by match score
        scored_recipes.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            "success": True,
            "recipes": scored_recipes[:10],  # Top 10 recipes
            "total_found": len(scored_recipes),
            "filters_applied": {
                "dietary_constraints": dietary_constraints or [],
                "cuisine_type": cuisine_type,
                "max_missing_ingredients": max_missing
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "recipes": []
        }


def _load_recipes(recipes_path: str) -> pd.DataFrame:
    """Load recipes from CSV database"""
    try:
        df = pd.read_csv(recipes_path)
        return df
    except FileNotFoundError:
        print(f"⚠ Recipe database not found at {recipes_path}")
        return pd.DataFrame()


def _filter_by_diet(df: pd.DataFrame, constraints: List[str]) -> pd.DataFrame:
    """Filter recipes by dietary constraints"""
    filtered = df.copy()
    
    for constraint in constraints:
        constraint_lower = constraint.lower().replace("-", "_").replace(" ", "_")
        
        # Check if column exists
        if constraint_lower in df.columns:
            filtered = filtered[filtered[constraint_lower] == True]
        elif 'dietary_tags' in df.columns:
            # Check in dietary_tags column
            filtered = filtered[
                filtered['dietary_tags'].str.contains(constraint_lower, case=False, na=False)
            ]
    
    return filtered


def _filter_by_cuisine(df: pd.DataFrame, cuisine: str) -> pd.DataFrame:
    """Filter recipes by cuisine type"""
    if 'cuisine' in df.columns:
        return df[df['cuisine'].str.contains(cuisine, case=False, na=False)]
    return df


def _score_recipes(
    df: pd.DataFrame,
    available_ingredients: List[str],
    max_missing: int
) -> List[Dict[str, Any]]:
    """Score recipes based on ingredient matching with fuzzy matching"""
    scored_recipes = []
    
    # Normalize available ingredients
    available_set = set(ing.lower().strip() for ing in available_ingredients)
    
    for _, recipe in df.iterrows():
        # Get required ingredients for this recipe
        required_ingredients = _parse_ingredients(recipe.get('ingredients', ''))
        required_set = set(ing.lower().strip() for ing in required_ingredients)
        
        # Calculate matches using fuzzy matching
        matched = set()
        for req_ing in required_set:
            for avail_ing in available_set:
                # Check if either ingredient contains the other (fuzzy match)
                if req_ing in avail_ing or avail_ing in req_ing:
                    matched.add(req_ing)
                    break
        
        missing = required_set.difference(matched)
        
        # Skip if too many missing ingredients
        if len(missing) > max_missing:
            continue
        
        # Calculate match score
        if len(required_set) > 0:
            match_percentage = len(matched) / len(required_set) * 100
        else:
            match_percentage = 0
        
        # Bonus points for having more matched ingredients
        bonus = len(matched) * 5  # 5% bonus per matched ingredient
        final_score = min(match_percentage + bonus, 100)
        
        scored_recipes.append({
            "name": recipe.get('name', 'Unknown'),
            "cuisine": recipe.get('cuisine', 'Unknown'),
            "ingredients": required_ingredients,
            "matched_ingredients": list(matched),
            "missing_ingredients": list(missing),
            "match_score": round(final_score, 1),
            "match_count": len(matched),
            "missing_count": len(missing),
            "calories": recipe.get('calories', 0),
            "protein_g": recipe.get('protein_g', 0),
            "carbs_g": recipe.get('carbs_g', 0),
            "fat_g": recipe.get('fat_g', 0),
            "prep_time": recipe.get('prep_time', 'Unknown'),
            "difficulty": recipe.get('difficulty', 'Medium')
        })
    
    return scored_recipes


def _parse_ingredients(ingredients_str: str) -> List[str]:
    """Parse ingredient string into list"""
    if pd.isna(ingredients_str):
        return []
    
    # Split by comma and clean
    ingredients = [
        ing.strip()
        for ing in str(ingredients_str).split(',')
        if ing.strip()
    ]
    
    return ingredients


# Create ADK FunctionTool wrapper
recipe_search_tool = FunctionTool(search_recipes)


if __name__ == "__main__":
    # Test the tool
    print("Testing Recipe Search Tool...")
    
    test_ingredients = ["tomato", "onion", "rice", "chicken"]
    result = search_recipes(test_ingredients, dietary_constraints=["vegetarian"])
    
    print(f"Success: {result.get('success')}")
    print(f"Found {result.get('total_found', 0)} recipes")
    if result.get('success'):
        for recipe in result.get('recipes', [])[:3]:
            print(f"  - {recipe['name']}: {recipe['match_score']}% match")
