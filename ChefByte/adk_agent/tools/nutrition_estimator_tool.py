"""
ADK Nutrition Estimator Tool - Calculate nutritional information for recipes
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from google.adk.tools import BaseTool
import pandas as pd
from typing import Dict, List, Any, Optional


class NutritionEstimatorTool(BaseTool):
    """
    ADK Tool for calculating nutritional information and selecting optimal meals
    """
    
    name = "nutrition_estimator"
    description = """
    Calculate nutritional information for recipes and select optimal meals based on calorie targets.
    Returns detailed nutrition data and meal recommendations.
    
    Use this tool when:
    - Need to calculate nutrition for specific recipes
    - User wants to hit a calorie target
    - Need to balance macros across multiple meals
    - Creating a meal plan with nutrition requirements
    """
    
    def __init__(self):
        super().__init__()
        self.nutrition_db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "nutrition.csv"
        )
    
    def execute(
        self,
        recipes: List[Dict[str, Any]],
        calorie_target: Optional[int] = None,
        meal_count: int = 3,
        protein_target: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate nutrition and select optimal meals
        
        Args:
            recipes: List of recipe dictionaries (from recipe_search_tool)
            calorie_target: Target daily calories (optional)
            meal_count: Number of meals to select
            protein_target: Target daily protein in grams (optional)
        
        Returns:
            Dictionary containing:
            - selected_meals: List of selected meal recipes
            - total_nutrition: Aggregated nutrition for selected meals
            - recommendations: Suggestions for balance
        """
        try:
            # Load nutrition database
            nutrition_db = self._load_nutrition_db()
            
            # Calculate nutrition for each recipe
            recipes_with_nutrition = []
            for recipe in recipes:
                nutrition = self._estimate_recipe_nutrition(recipe, nutrition_db)
                recipe_copy = recipe.copy()
                recipe_copy['detailed_nutrition'] = nutrition
                recipes_with_nutrition.append(recipe_copy)
            
            # Select optimal meals based on targets
            selected_meals = self._select_optimal_meals(
                recipes_with_nutrition,
                calorie_target,
                meal_count,
                protein_target
            )
            
            # Calculate total nutrition
            total_nutrition = self._calculate_total_nutrition(selected_meals)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
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
    
    def _load_nutrition_db(self) -> pd.DataFrame:
        """Load nutrition database"""
        try:
            df = pd.read_csv(self.nutrition_db_path)
            return df
        except FileNotFoundError:
            print(f"⚠ Nutrition database not found at {self.nutrition_db_path}")
            return pd.DataFrame()
    
    def _estimate_recipe_nutrition(
        self,
        recipe: Dict[str, Any],
        nutrition_db: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Estimate nutrition for a recipe based on ingredients
        
        Args:
            recipe: Recipe dictionary with ingredients
            nutrition_db: Nutrition database DataFrame
        
        Returns:
            Dictionary with nutrition values
        """
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
        
        # Otherwise, estimate from ingredients
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        ingredients = recipe.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [ing.strip() for ing in ingredients.split(',')]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower().strip()
            
            # Look up in nutrition database
            match = nutrition_db[
                nutrition_db['ingredient'].str.lower().str.contains(ingredient_lower, na=False)
            ]
            
            if not match.empty:
                # Use first match (assuming 100g serving)
                row = match.iloc[0]
                total_calories += row.get('calories_per_100g', 0)
                total_protein += row.get('protein_per_100g', 0)
                total_carbs += row.get('carbs_per_100g', 0)
                total_fat += row.get('fat_per_100g', 0)
                total_fiber += row.get('fiber_per_100g', 0)
        
        return {
            'calories': round(total_calories, 1),
            'protein_g': round(total_protein, 1),
            'carbs_g': round(total_carbs, 1),
            'fat_g': round(total_fat, 1),
            'fiber_g': round(total_fiber, 1),
            'source': 'estimated'
        }
    
    def _select_optimal_meals(
        self,
        recipes: List[Dict[str, Any]],
        calorie_target: Optional[int],
        meal_count: int,
        protein_target: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Select optimal combination of meals
        
        Simple greedy algorithm:
        1. Sort by match_score
        2. Select top recipes that fit within calorie target
        3. Prioritize variety (different cuisines/types)
        """
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
            
            # Check calorie constraint
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
    
    def _calculate_total_nutrition(self, meals: List[Dict[str, Any]]) -> Dict[str, float]:
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
        self,
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
                recommendations.append(f"⚠ Below calorie target by {int(-calorie_diff)} cal. Consider adding a snack.")
        
        # Protein recommendations
        if protein_target:
            protein_diff = total_nutrition['protein_g'] - protein_target
            if abs(protein_diff) < 10:
                recommendations.append("✓ Protein target met!")
            elif protein_diff < -10:
                recommendations.append(f"⚠ Need {int(-protein_diff)}g more protein. Add dal, paneer, or chicken.")
        
        # Macro balance recommendations
        total_macros = total_nutrition['protein_g'] + total_nutrition['carbs_g'] + total_nutrition['fat_g']
        if total_macros > 0:
            protein_pct = (total_nutrition['protein_g'] * 4 / total_nutrition['calories']) * 100 if total_nutrition['calories'] > 0 else 0
            
            if protein_pct < 15:
                recommendations.append("💪 Consider adding more protein-rich foods")
            elif protein_pct > 35:
                recommendations.append("🌾 Consider adding more carbs for energy")
        
        # Fiber recommendation
        if total_nutrition['fiber_g'] < 10:
            recommendations.append("🥗 Add more vegetables or whole grains for fiber")
        
        return recommendations


# Create tool instance for ADK registration
nutrition_estimator_tool = NutritionEstimatorTool()


# Standalone function for backward compatibility
def calculate_nutrition(
    recipes: List[Dict[str, Any]],
    calorie_target: Optional[int] = None,
    meal_count: int = 3
):
    """Standalone function wrapper for ADK tool"""
    return nutrition_estimator_tool.execute(recipes, calorie_target, meal_count)


if __name__ == "__main__":
    # Test the tool
    print("Testing ADK Nutrition Estimator Tool...")
    
    test_recipes = [
        {
            "name": "Palak Paneer",
            "calories": 520,
            "protein_g": 22,
            "carbs_g": 18,
            "fat_g": 40
        }
    ]
    
    result = nutrition_estimator_tool.execute(test_recipes, calorie_target=1800)
    print(f"Success: {result.get('success')}")
    print(f"Total calories: {result.get('total_nutrition', {}).get('calories')}")
