"""
ADK Nutrition Estimator Tool - Calculate nutrition and select optimal meals (FunctionTool)
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from google.adk.tools import FunctionTool
import pandas as pd
from typing import Dict, List, Any, Optional
from difflib import get_close_matches


def estimate_nutrition(
    recipes: List[Dict[str, Any]],
    calorie_target: Optional[int] = None,
    meal_count: int = 3,
    protein_target: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate nutritional information for recipes and select optimal meals based on targets.
    Returns detailed nutrition data, selected meals, and dietary recommendations.
    
    Use this tool when you need to:
    - Calculate total nutrition for a set of recipes
    - Select meals that meet calorie or protein targets
    - Get balanced meal recommendations
    - Plan meals with specific nutritional goals
    
    Args:
        recipes: List of recipe dictionaries from recipe_search (must have 'name' and ingredient info)
        calorie_target: Target daily calories (e.g., 1800, 2000) - optional
        meal_count: Number of meals to select (default: 3)
        protein_target: Target daily protein in grams (e.g., 80, 100) - optional
    
    Returns:
        Dictionary with:
        - selected_meals: Best meal combination meeting targets
        - total_nutrition: Aggregated calories, protein, carbs, fat, fiber
        - recommendations: Tips for better balance
        - meal_count: Number of meals selected
    """
    try:
        # Get cleaned ingredients database path (9,318 ingredients with precise nutrition)
        ingredients_db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "cleaned_ingredients.csv"
        )
        
        # Load precise ingredient nutrition database
        nutrition_db = _load_ingredient_nutrition_db(ingredients_db_path)
        
        # Calculate nutrition for each recipe
        recipes_with_nutrition = []
        for recipe in recipes:
            nutrition = _estimate_recipe_nutrition(recipe, nutrition_db)
            recipe_copy = recipe.copy()
            recipe_copy['detailed_nutrition'] = nutrition
            recipes_with_nutrition.append(recipe_copy)
        
        # Select optimal meals based on targets
        selected_meals = _select_optimal_meals(
            recipes_with_nutrition,
            calorie_target,
            meal_count,
            protein_target
        )
        
        # Calculate total nutrition
        total_nutrition = _calculate_total_nutrition(selected_meals)
        
        # Generate recommendations
        recommendations = _generate_recommendations(
            total_nutrition,
            calorie_target,
            protein_target
        )
        
        return {
            "success": True,
            "selected_meals": selected_meals,
            "total_nutrition": total_nutrition,
            "recommendations": recommendations,
            "meal_count": len(selected_meals)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "selected_meals": []
        }


def _load_ingredient_nutrition_db(db_path: str) -> pd.DataFrame:
    """Load cleaned ingredients nutrition database with 9,318 ingredients"""
    try:
        df = pd.read_csv(db_path)
        # Normalize ingredient names for matching
        df['ingredient_lower'] = df['Descrip'].str.lower().str.strip()
        print(f"✓ Loaded {len(df)} ingredients with precise nutrition data")
        return df
    except FileNotFoundError:
        print(f"⚠ Ingredient nutrition database not found at {db_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"⚠ Error loading nutrition database: {e}")
        return pd.DataFrame()


def _estimate_recipe_nutrition(
    recipe: Dict[str, Any],
    nutrition_db: pd.DataFrame
) -> Dict[str, float]:
    """Estimate nutrition for a recipe based on ingredients"""
    # If recipe already has nutrition data, use it
    if all(key in recipe for key in ['calories', 'protein_g', 'carbs_g', 'fat_g']):
        return {
            'calories': recipe.get('calories', 0),
            'protein_g': recipe.get('protein_g', 0),
            'carbs_g': recipe.get('carbs_g', 0),
            'fat_g': recipe.get('fat_g', 0),
            'fiber_g': recipe.get('fiber_g', 0),
            'source': 'recipe_data'
        }
    
    # Otherwise, estimate from ingredients using precise database
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_fiber = 0
    matched_count = 0
    
    ingredients = recipe.get('ingredients', [])
    if isinstance(ingredients, str):
        ingredients = [ing.strip() for ing in ingredients.split(',')]
    
    # Create lookup dictionary for faster fuzzy matching
    if not nutrition_db.empty and 'ingredient_lower' in nutrition_db.columns:
        ingredient_names = nutrition_db['ingredient_lower'].tolist()
    else:
        ingredient_names = []
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower().strip()
        
        # Try exact match first
        exact_match = nutrition_db[
            nutrition_db['ingredient_lower'] == ingredient_lower
        ]
        
        if not exact_match.empty:
            row = exact_match.iloc[0]
            # Assume 100g serving per ingredient
            total_calories += row.get('Energy_kcal', 0)
            total_protein += row.get('Protein_g', 0)
            total_carbs += row.get('Carb_g', 0)
            total_fat += row.get('Fat_g', 0)
            total_fiber += row.get('Fiber_g', 0)
            matched_count += 1
        else:
            # Try fuzzy matching for ingredient variations
            fuzzy_matches = get_close_matches(
                ingredient_lower,
                ingredient_names,
                n=1,
                cutoff=0.6
            )
            
            if fuzzy_matches:
                match = nutrition_db[
                    nutrition_db['ingredient_lower'] == fuzzy_matches[0]
                ]
                if not match.empty:
                    row = match.iloc[0]
                    total_calories += row.get('Energy_kcal', 0)
                    total_protein += row.get('Protein_g', 0)
                    total_carbs += row.get('Carb_g', 0)
                    total_fat += row.get('Fat_g', 0)
                    total_fiber += row.get('Fiber_g', 0)
                    matched_count += 1
    
    # Calculate match confidence
    total_ingredients = len(ingredients) if ingredients else 1
    match_confidence = (matched_count / total_ingredients) * 100 if total_ingredients > 0 else 0
    
    return {
        'calories': round(total_calories, 1),
        'protein_g': round(total_protein, 1),
        'carbs_g': round(total_carbs, 1),
        'fat_g': round(total_fat, 1),
        'fiber_g': round(total_fiber, 1),
        'source': 'precise_database',
        'matched_ingredients': matched_count,
        'total_ingredients': total_ingredients,
        'confidence': round(match_confidence, 1)
    }


def _select_optimal_meals(
    recipes: List[Dict[str, Any]],
    calorie_target: Optional[int],
    meal_count: int,
    protein_target: Optional[int]
) -> List[Dict[str, Any]]:
    """Select optimal combination of meals using greedy algorithm"""
    if not recipes:
        return []
    
    # Sort by match score
    sorted_recipes = sorted(
        recipes,
        key=lambda x: x.get('match_score', 0),
        reverse=True
    )
    
    selected = []
    total_calories = 0
    used_names = set()
    
    for recipe in sorted_recipes:
        # Skip if already selected
        if recipe['name'] in used_names:
            continue
        
        recipe_calories = recipe.get('calories', recipe.get('detailed_nutrition', {}).get('calories', 0))
        
        # Check calorie constraint (allow 10% overage)
        if calorie_target and (total_calories + recipe_calories > calorie_target * 1.1):
            continue
        
        # Add to selection
        selected.append(recipe)
        total_calories += recipe_calories
        used_names.add(recipe['name'])
        
        # Stop when we have enough meals
        if len(selected) >= meal_count:
            break
    
    return selected


def _calculate_total_nutrition(meals: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate total nutrition across selected meals"""
    total = {
        'calories': 0,
        'protein_g': 0,
        'carbs_g': 0,
        'fat_g': 0,
        'fiber_g': 0
    }
    
    for meal in meals:
        nutrition = meal.get('detailed_nutrition', {})
        if not nutrition:
            # Fallback to direct recipe data
            nutrition = {
                'calories': meal.get('calories', 0),
                'protein_g': meal.get('protein_g', 0),
                'carbs_g': meal.get('carbs_g', 0),
                'fat_g': meal.get('fat_g', 0),
                'fiber_g': meal.get('fiber_g', 0)
            }
        
        for key in total.keys():
            total[key] += nutrition.get(key, 0)
    
    # Round values
    return {k: round(v, 1) for k, v in total.items()}


def _generate_recommendations(
    total_nutrition: Dict[str, float],
    calorie_target: Optional[int],
    protein_target: Optional[int]
) -> List[str]:
    """Generate dietary recommendations based on nutrition analysis"""
    recommendations = []
    
    # Calorie recommendations
    if calorie_target:
        calorie_diff = total_nutrition['calories'] - calorie_target
        if abs(calorie_diff) < 100:
            recommendations.append("✓ Calorie target met perfectly!")
        elif calorie_diff > 100:
            recommendations.append(f"⚠ Exceeds calorie target by {int(calorie_diff)} cal. Consider smaller portions.")
        else:
            recommendations.append(f"⚠ Below calorie target by {int(-calorie_diff)} cal. Consider adding a healthy snack.")
    
    # Protein recommendations
    if protein_target:
        protein_diff = total_nutrition['protein_g'] - protein_target
        if abs(protein_diff) < 10:
            recommendations.append("✓ Protein target met!")
        elif protein_diff < -10:
            recommendations.append(f"⚠ Need {int(-protein_diff)}g more protein. Add dal, paneer, chicken, or yogurt.")
    
    # Macro balance recommendations
    if total_nutrition['calories'] > 0:
        protein_pct = (total_nutrition['protein_g'] * 4 / total_nutrition['calories']) * 100
        
        if protein_pct < 15:
            recommendations.append("💪 Consider adding more protein-rich foods (dal, paneer, eggs)")
        elif protein_pct > 35:
            recommendations.append("🌾 Consider adding more carbs for energy (rice, roti, oats)")
    
    # Fiber recommendation
    if total_nutrition['fiber_g'] < 10:
        recommendations.append("🥗 Add more fiber: vegetables, fruits, or whole grains")
    
    if not recommendations:
        recommendations.append("✓ Well-balanced meal plan!")
    
    return recommendations


# Create ADK FunctionTool wrapper
nutrition_estimator_tool = FunctionTool(estimate_nutrition)


if __name__ == "__main__":
    # Test the tool
    print("Testing Nutrition Estimator Tool...")
    
    test_recipes = [
        {
            "name": "Palak Paneer",
            "calories": 520,
            "protein_g": 22,
            "carbs_g": 18,
            "fat_g": 40,
            "match_score": 95
        },
        {
            "name": "Jeera Rice",
            "calories": 380,
            "protein_g": 8,
            "carbs_g": 75,
            "fat_g": 5,
            "match_score": 90
        }
    ]
    
    result = estimate_nutrition(test_recipes, calorie_target=1800, meal_count=2)
    print(f"Success: {result.get('success')}")
    print(f"Total calories: {result.get('total_nutrition', {}).get('calories')}")
    print(f"Recommendations: {result.get('recommendations')}")
