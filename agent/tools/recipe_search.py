"""
Recipe Search - Filters recipes based on available ingredients and constraints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from gemini_setup import get_gemini_model


def search_recipes(available_ingredients, dietary_constraints=None, max_missing=2):
    """
    Search for recipes that match available ingredients and constraints
    
    Args:
        available_ingredients: List of available ingredient names
        dietary_constraints: List of dietary requirements (e.g., ['vegetarian', 'gluten-free'])
        max_missing: Maximum number of missing ingredients allowed
    
    Returns:
        List of matching recipes with match scores
    """
    try:
        # Load recipes database
        recipes_df = _load_recipes()
        
        if recipes_df.empty:
            print("⚠ No recipes found in database")
            return []
        
        # Filter by dietary constraints
        if dietary_constraints:
            recipes_df = _filter_by_diet(recipes_df, dietary_constraints)
        
        # Score recipes by ingredient match
        scored_recipes = _score_recipes(recipes_df, available_ingredients, max_missing)
        
        # Sort by match score
        scored_recipes.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"✓ Found {len(scored_recipes)} matching recipes")
        return scored_recipes[:20]  # Return top 20
        
    except Exception as e:
        print(f"✗ Error searching recipes: {str(e)}")
        return []


def _load_recipes():
    """
    Load recipes from CSV file
    
    Returns:
        DataFrame with recipe data
    """
    try:
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data',
            'recipes.csv'
        )
        
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            return df
        else:
            print(f"⚠ Recipe file not found at {data_path}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"✗ Error loading recipes: {str(e)}")
        return pd.DataFrame()


def _filter_by_diet(recipes_df, dietary_constraints):
    """
    Filter recipes by dietary constraints
    
    Args:
        recipes_df: DataFrame with recipes
        dietary_constraints: List of constraints
    
    Returns:
        Filtered DataFrame
    """
    filtered = recipes_df.copy()
    
    for constraint in dietary_constraints:
        constraint_lower = constraint.lower()
        
        # Check if constraint column exists
        if constraint_lower in filtered.columns:
            filtered = filtered[filtered[constraint_lower] == True]
        elif 'tags' in filtered.columns:
            # Check in tags column
            filtered = filtered[filtered['tags'].str.contains(constraint_lower, case=False, na=False)]
    
    return filtered


def _score_recipes(recipes_df, available_ingredients, max_missing):
    """
    Score recipes based on ingredient match
    
    Args:
        recipes_df: DataFrame with recipes
        available_ingredients: List of available ingredients
        max_missing: Max missing ingredients
    
    Returns:
        List of scored recipes
    """
    scored_recipes = []
    available_set = set(ing.lower() for ing in available_ingredients)
    
    for _, recipe in recipes_df.iterrows():
        # Parse recipe ingredients
        recipe_ingredients = _parse_recipe_ingredients(recipe.get('ingredients', ''))
        recipe_set = set(ing.lower() for ing in recipe_ingredients)
        
        # Calculate match
        matched = recipe_set.intersection(available_set)
        missing = recipe_set - available_set
        
        # Skip if too many missing ingredients
        if len(missing) > max_missing:
            continue
        
        # Calculate match score
        match_percentage = len(matched) / len(recipe_set) if recipe_set else 0
        match_score = match_percentage * 100
        
        scored_recipes.append({
            'name': recipe.get('name', 'Unknown Recipe'),
            'ingredients': recipe_ingredients,
            'matched_ingredients': list(matched),
            'missing_ingredients': list(missing),
            'match_score': round(match_score, 2),
            'match_percentage': f"{match_percentage*100:.1f}%",
            'instructions': recipe.get('instructions', ''),
            'prep_time': recipe.get('prep_time', 'Unknown'),
            'cook_time': recipe.get('cook_time', 'Unknown'),
            'servings': recipe.get('servings', 'Unknown'),
            'tags': recipe.get('tags', '')
        })
    
    return scored_recipes


def _parse_recipe_ingredients(ingredients_str):
    """
    Parse ingredient string into list
    
    Args:
        ingredients_str: Comma-separated string of ingredients
    
    Returns:
        List of ingredient names
    """
    if pd.isna(ingredients_str) or not ingredients_str:
        return []
    
    # Split by comma and clean
    ingredients = [ing.strip() for ing in str(ingredients_str).split(',')]
    return [ing for ing in ingredients if ing]


def get_recipe_suggestions_with_gemini(available_ingredients, recipes):
    """
    Use Gemini to provide intelligent recipe suggestions
    
    Args:
        available_ingredients: List of available ingredients
        recipes: List of filtered recipes
    
    Returns:
        Enhanced suggestions with reasoning
    """
    try:
        model = get_gemini_model("gemini-pro")
        
        prompt = f"""
You are a chef AI assistant. Given these available ingredients and recipes, 
provide the top 5 recipe recommendations with reasoning.

AVAILABLE INGREDIENTS:
{', '.join(available_ingredients)}

RECIPES TO CHOOSE FROM:
{_format_recipes_for_prompt(recipes[:10])}

For each recommended recipe, explain:
1. Why it's a good match
2. What makes it special
3. Any suggested substitutions for missing ingredients

Format as a numbered list with clear explanations.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"✗ Error getting Gemini suggestions: {str(e)}")
        return "Unable to generate suggestions"


def _format_recipes_for_prompt(recipes):
    """Format recipes for Gemini prompt"""
    formatted = []
    for i, recipe in enumerate(recipes, 1):
        formatted.append(
            f"{i}. {recipe['name']} - Match: {recipe['match_percentage']}, "
            f"Missing: {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'none'}"
        )
    return '\n'.join(formatted)


# Example usage
if __name__ == "__main__":
    # Test recipe search
    test_ingredients = ['chicken', 'tomatoes', 'rice', 'onion', 'garlic']
    test_constraints = ['gluten-free']
    
    print("Searching for recipes...")
    print(f"Ingredients: {', '.join(test_ingredients)}")
    print(f"Constraints: {', '.join(test_constraints)}")
    print("="*50)
    
    recipes = search_recipes(test_ingredients, test_constraints, max_missing=2)
    
    print(f"\nFound {len(recipes)} recipes:\n")
    for i, recipe in enumerate(recipes[:5], 1):
        print(f"{i}. {recipe['name']}")
        print(f"   Match: {recipe['match_percentage']}")
        print(f"   Matched: {', '.join(recipe['matched_ingredients'][:3])}...")
        print(f"   Missing: {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'none'}")
        print()
