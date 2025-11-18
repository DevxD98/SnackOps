"""
Nutrition Estimator - Calculates nutritional information for recipes and meal plans
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from gemini_setup import get_gemini_model


def calculate_nutrition(recipes, calorie_target=None, meal_count=3):
    """
    Calculate nutrition for recipes and select optimal meals
    
    Args:
        recipes: List of recipe dictionaries
        calorie_target: Target daily calories
        meal_count: Number of meals to select
    
    Returns:
        Dictionary with nutrition data and selected meals
    """
    try:
        # Load nutrition database
        nutrition_db = _load_nutrition_db()
        
        # Calculate nutrition for each recipe
        recipes_with_nutrition = []
        for recipe in recipes:
            nutrition = _estimate_recipe_nutrition(recipe, nutrition_db)
            recipe['nutrition'] = nutrition
            recipes_with_nutrition.append(recipe)
        
        # Select optimal meals based on calorie target
        selected_meals = _select_optimal_meals(
            recipes_with_nutrition,
            calorie_target,
            meal_count
        )
        
        # Calculate total nutrition
        total_nutrition = _calculate_total_nutrition(selected_meals)
        
        print(f"✓ Calculated nutrition for {len(recipes_with_nutrition)} recipes")
        
        return {
            'selected_meals': selected_meals,
            'total_nutrition': total_nutrition,
            'calories_per_meal': total_nutrition['calories'] / meal_count if meal_count > 0 else 0,
            'all_recipes_nutrition': recipes_with_nutrition
        }
        
    except Exception as e:
        print(f"✗ Error calculating nutrition: {str(e)}")
        return {
            'selected_meals': recipes[:meal_count],
            'total_nutrition': {},
            'calories_per_meal': 0
        }


def _load_nutrition_db():
    """
    Load nutrition database
    
    Returns:
        DataFrame with nutrition data
    """
    try:
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data',
            'nutrition.csv'
        )
        
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            return df
        else:
            print(f"⚠ Nutrition file not found, using estimates")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"✗ Error loading nutrition database: {str(e)}")
        return pd.DataFrame()


def _estimate_recipe_nutrition(recipe, nutrition_db):
    """
    Estimate nutrition for a single recipe
    
    Args:
        recipe: Recipe dictionary
        nutrition_db: Nutrition database DataFrame
    
    Returns:
        Dictionary with nutritional information
    """
    # If nutrition DB is available, use it
    if not nutrition_db.empty:
        return _calculate_from_db(recipe, nutrition_db)
    else:
        # Use Gemini for estimation
        return _estimate_with_gemini(recipe)


def _calculate_from_db(recipe, nutrition_db):
    """
    Calculate nutrition from database
    
    Args:
        recipe: Recipe dictionary
        nutrition_db: Nutrition database
    
    Returns:
        Nutrition dictionary
    """
    total_nutrition = {
        'calories': 0,
        'protein_g': 0,
        'carbs_g': 0,
        'fat_g': 0,
        'fiber_g': 0
    }
    
    ingredients = recipe.get('ingredients', [])
    
    for ingredient in ingredients:
        # Look up in database
        ing_lower = ingredient.lower()
        match = nutrition_db[nutrition_db['ingredient'].str.lower() == ing_lower]
        
        if not match.empty:
            # Add nutrition values
            total_nutrition['calories'] += match.iloc[0].get('calories', 0)
            total_nutrition['protein_g'] += match.iloc[0].get('protein_g', 0)
            total_nutrition['carbs_g'] += match.iloc[0].get('carbs_g', 0)
            total_nutrition['fat_g'] += match.iloc[0].get('fat_g', 0)
            total_nutrition['fiber_g'] += match.iloc[0].get('fiber_g', 0)
    
    # Adjust by servings
    servings = recipe.get('servings', 1)
    if servings and servings != 'Unknown':
        try:
            servings_num = int(servings)
            for key in total_nutrition:
                total_nutrition[key] = round(total_nutrition[key] / servings_num, 2)
        except:
            pass
    
    return total_nutrition


def _estimate_with_gemini(recipe):
    """
    Use Gemini to estimate nutrition
    
    Args:
        recipe: Recipe dictionary
    
    Returns:
        Nutrition dictionary
    """
    try:
        model = get_gemini_model("gemini-2.5-flash")
        
        ingredients_str = ', '.join(recipe.get('ingredients', []))
        
        prompt = f"""
Estimate the nutritional information per serving for this recipe:

RECIPE: {recipe.get('name', 'Unknown')}
INGREDIENTS: {ingredients_str}
SERVINGS: {recipe.get('servings', '1')}

Provide estimates for ONE SERVING in this exact format:
Calories: X
Protein: X g
Carbs: X g
Fat: X g
Fiber: X g

Be realistic and base estimates on typical portion sizes.
        """
        
        response = model.generate_content(prompt)
        
        # Parse response
        nutrition = _parse_nutrition_response(response.text)
        return nutrition
        
    except Exception as e:
        print(f"⚠ Error estimating nutrition with Gemini: {str(e)}")
        # Return default estimates
        return {
            'calories': 400,
            'protein_g': 20,
            'carbs_g': 40,
            'fat_g': 15,
            'fiber_g': 5
        }


def _parse_nutrition_response(response_text):
    """
    Parse nutrition from Gemini response
    
    Args:
        response_text: Raw response text
    
    Returns:
        Nutrition dictionary
    """
    nutrition = {
        'calories': 0,
        'protein_g': 0,
        'carbs_g': 0,
        'fat_g': 0,
        'fiber_g': 0
    }
    
    lines = response_text.strip().split('\n')
    for line in lines:
        line_lower = line.lower()
        
        if 'calories:' in line_lower:
            try:
                nutrition['calories'] = float(line.split(':')[1].strip().replace('g', '').strip())
            except:
                pass
        elif 'protein:' in line_lower:
            try:
                nutrition['protein_g'] = float(line.split(':')[1].strip().replace('g', '').strip())
            except:
                pass
        elif 'carbs:' in line_lower or 'carbohydrates:' in line_lower:
            try:
                nutrition['carbs_g'] = float(line.split(':')[1].strip().replace('g', '').strip())
            except:
                pass
        elif 'fat:' in line_lower:
            try:
                nutrition['fat_g'] = float(line.split(':')[1].strip().replace('g', '').strip())
            except:
                pass
        elif 'fiber:' in line_lower:
            try:
                nutrition['fiber_g'] = float(line.split(':')[1].strip().replace('g', '').strip())
            except:
                pass
    
    return nutrition


def _select_optimal_meals(recipes, calorie_target, meal_count):
    """
    Select optimal meals based on nutrition goals
    
    Args:
        recipes: List of recipes with nutrition
        calorie_target: Daily calorie target
        meal_count: Number of meals to select
    
    Returns:
        List of selected recipes
    """
    if not recipes:
        return []
    
    # If no calorie target, just take top recipes by match score
    if not calorie_target:
        return recipes[:meal_count]
    
    # Calculate target calories per meal
    calories_per_meal = calorie_target / meal_count
    
    # Score recipes by how close they are to target
    for recipe in recipes:
        recipe_calories = recipe['nutrition'].get('calories', 400)
        calorie_diff = abs(recipe_calories - calories_per_meal)
        
        # Combine match score with calorie proximity
        # Lower calorie diff is better
        calorie_score = max(0, 100 - (calorie_diff / 10))
        combined_score = (recipe['match_score'] * 0.7) + (calorie_score * 0.3)
        recipe['combined_score'] = combined_score
    
    # Sort by combined score
    recipes.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
    
    return recipes[:meal_count]


def _calculate_total_nutrition(meals):
    """
    Calculate total nutrition across all meals
    
    Args:
        meals: List of meal dictionaries
    
    Returns:
        Total nutrition dictionary
    """
    total = {
        'calories': 0,
        'protein_g': 0,
        'carbs_g': 0,
        'fat_g': 0,
        'fiber_g': 0
    }
    
    for meal in meals:
        nutrition = meal.get('nutrition', {})
        for key in total:
            total[key] += nutrition.get(key, 0)
    
    # Round values
    for key in total:
        total[key] = round(total[key], 2)
    
    return total


# Example usage
if __name__ == "__main__":
    # Test with sample recipes
    test_recipes = [
        {
            'name': 'Chicken Stir Fry',
            'ingredients': ['chicken', 'broccoli', 'rice', 'soy sauce'],
            'match_score': 95,
            'servings': 2
        },
        {
            'name': 'Tomato Pasta',
            'ingredients': ['pasta', 'tomatoes', 'garlic', 'basil'],
            'match_score': 85,
            'servings': 2
        },
        {
            'name': 'Greek Salad',
            'ingredients': ['lettuce', 'tomatoes', 'cucumber', 'feta'],
            'match_score': 75,
            'servings': 1
        }
    ]
    
    print("Calculating nutrition...")
    print("="*50)
    
    result = calculate_nutrition(test_recipes, calorie_target=2000, meal_count=3)
    
    print("\nSelected Meals:")
    for i, meal in enumerate(result['selected_meals'], 1):
        print(f"\n{i}. {meal['name']}")
        print(f"   Calories: {meal['nutrition']['calories']}")
        print(f"   Protein: {meal['nutrition']['protein_g']}g")
        print(f"   Carbs: {meal['nutrition']['carbs_g']}g")
        print(f"   Fat: {meal['nutrition']['fat_g']}g")
    
    print("\n\nTotal Daily Nutrition:")
    print("="*50)
    for key, value in result['total_nutrition'].items():
        print(f"{key}: {value}")
