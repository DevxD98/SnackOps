"""
ADK Recipe Search Tool - Find recipes matching available ingredients
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from google.adk.tools import BaseTool
import pandas as pd
from gemini_setup import get_gemini_model
from typing import Dict, List, Any, Optional


class RecipeSearchTool(BaseTool):
    """
    ADK Tool for searching recipes based on available ingredients and dietary constraints
    """
    
    name = "recipe_search"
    description = """
    Search for recipes that match available ingredients and dietary constraints.
    Returns a list of recipes with match scores, missing ingredients, and recipe details.
    
    Use this tool when:
    - User has a list of available ingredients
    - Need to find recipes that can be made with available items
    - User wants recipes with minimal missing ingredients
    - Need to filter by dietary constraints (vegetarian, vegan, gluten-free, etc.)
    """
    
    def __init__(self):
        super().__init__()
        self.model = get_gemini_model()
        self.recipes_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "recipes.csv"
        )
    
    def execute(
        self,
        available_ingredients: List[str],
        dietary_constraints: Optional[List[str]] = None,
        max_missing: int = 2,
        cuisine_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for recipes matching criteria
        
        Args:
            available_ingredients: List of available ingredient names
            dietary_constraints: List of dietary requirements (e.g., ['vegetarian', 'gluten-free'])
            max_missing: Maximum number of missing ingredients allowed
            cuisine_type: Optional cuisine filter (e.g., 'indian', 'punjabi', 'south_indian')
        
        Returns:
            Dictionary containing:
            - recipes: List of matching recipes with scores
            - total_found: Number of recipes found
            - filters_applied: Summary of filters used
        """
        try:
            # Load recipes database
            recipes_df = self._load_recipes()
            
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
                filtered_df = self._filter_by_diet(filtered_df, dietary_constraints)
            
            # Filter by cuisine type
            if cuisine_type:
                filtered_df = self._filter_by_cuisine(filtered_df, cuisine_type)
            
            # Score recipes by ingredient match
            scored_recipes = self._score_recipes(
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
    
    def _load_recipes(self) -> pd.DataFrame:
        """Load recipes from CSV database"""
        try:
            df = pd.read_csv(self.recipes_path)
            return df
        except FileNotFoundError:
            print(f"⚠ Recipe database not found at {self.recipes_path}")
            return pd.DataFrame()
    
    def _filter_by_diet(self, df: pd.DataFrame, constraints: List[str]) -> pd.DataFrame:
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
    
    def _filter_by_cuisine(self, df: pd.DataFrame, cuisine: str) -> pd.DataFrame:
        """Filter recipes by cuisine type"""
        if 'cuisine' in df.columns:
            return df[df['cuisine'].str.contains(cuisine, case=False, na=False)]
        return df
    
    def _score_recipes(
        self,
        df: pd.DataFrame,
        available_ingredients: List[str],
        max_missing: int
    ) -> List[Dict[str, Any]]:
        """
        Score recipes based on ingredient matching
        
        Args:
            df: DataFrame with recipes
            available_ingredients: List of available ingredients
            max_missing: Maximum missing ingredients allowed
        
        Returns:
            List of recipe dictionaries with match scores
        """
        scored_recipes = []
        
        # Normalize available ingredients
        available_set = set(ing.lower().strip() for ing in available_ingredients)
        
        for _, recipe in df.iterrows():
            # Get required ingredients for this recipe
            required_ingredients = self._parse_ingredients(recipe.get('ingredients', ''))
            required_set = set(ing.lower().strip() for ing in required_ingredients)
            
            # Calculate matches and missing
            matched = required_set.intersection(available_set)
            missing = required_set.difference(available_set)
            
            # Skip if too many missing ingredients
            if len(missing) > max_missing:
                continue
            
            # Calculate match score
            if len(required_set) > 0:
                match_percentage = len(matched) / len(required_set) * 100
            else:
                match_percentage = 0
            
            scored_recipes.append({
                "name": recipe.get('name', 'Unknown'),
                "cuisine": recipe.get('cuisine', 'Unknown'),
                "ingredients": required_ingredients,
                "matched_ingredients": list(matched),
                "missing_ingredients": list(missing),
                "match_score": round(match_percentage, 1),
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
    
    def _parse_ingredients(self, ingredients_str: str) -> List[str]:
        """
        Parse ingredient string into list
        
        Args:
            ingredients_str: Comma-separated ingredient string
        
        Returns:
            List of ingredient names
        """
        if pd.isna(ingredients_str):
            return []
        
        # Split by comma and clean
        ingredients = [
            ing.strip()
            for ing in str(ingredients_str).split(',')
            if ing.strip()
        ]
        
        return ingredients


# Create tool instance for ADK registration
recipe_search_tool = RecipeSearchTool()


# Standalone function for backward compatibility
def search_recipes(
    available_ingredients: List[str],
    dietary_constraints: Optional[List[str]] = None,
    max_missing: int = 2
):
    """Standalone function wrapper for ADK tool"""
    return recipe_search_tool.execute(
        available_ingredients,
        dietary_constraints,
        max_missing
    )


if __name__ == "__main__":
    # Test the tool
    print("Testing ADK Recipe Search Tool...")
    
    test_ingredients = ["tomato", "onion", "rice", "chicken"]
    result = recipe_search_tool.execute(test_ingredients)
    
    print(f"Found {result.get('total_found', 0)} recipes")
    if result.get('success'):
        for recipe in result.get('recipes', [])[:3]:
            print(f"  - {recipe['name']}: {recipe['match_score']}% match")
