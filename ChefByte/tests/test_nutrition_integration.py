"""
Test nutrition estimator with cleaned_ingredients.csv integration
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adk_agent.tools.nutrition_estimator_adk import estimate_nutrition


def test_nutrition_calculation():
    """Test nutrition calculation with sample recipes"""
    
    # Sample recipes with common ingredients
    test_recipes = [
        {
            "name": "Egg Bhurji",
            "ingredients": ["eggs", "onion", "tomato", "butter", "salt"],
            "match_score": 95
        },
        {
            "name": "Dal Rice",
            "ingredients": ["lentils", "rice", "butter", "salt"],
            "match_score": 90
        },
        {
            "name": "Paneer Tikka",
            "ingredients": ["cheese cheddar", "yogurt", "garlic", "pepper"],
            "match_score": 85
        }
    ]
    
    print("=" * 60)
    print("TESTING NUTRITION ESTIMATOR WITH CLEANED INGREDIENTS")
    print("=" * 60)
    
    # Test without targets
    print("\n1. Testing basic nutrition calculation...")
    result = estimate_nutrition(recipes=test_recipes, meal_count=3)
    
    if result['success']:
        print(f"✓ Success! Selected {result['meal_count']} meals")
        print(f"\nTotal Nutrition:")
        for key, value in result['total_nutrition'].items():
            print(f"  {key}: {value}")
        
        print(f"\nSelected Meals:")
        for i, meal in enumerate(result['selected_meals'], 1):
            nutrition = meal.get('detailed_nutrition', {})
            print(f"\n  {i}. {meal['name']}")
            print(f"     Calories: {nutrition.get('calories', 0)} kcal")
            print(f"     Protein: {nutrition.get('protein_g', 0)}g")
            print(f"     Carbs: {nutrition.get('carbs_g', 0)}g")
            print(f"     Fat: {nutrition.get('fat_g', 0)}g")
            print(f"     Confidence: {nutrition.get('confidence', 0)}%")
            print(f"     Matched: {nutrition.get('matched_ingredients', 0)}/{nutrition.get('total_ingredients', 0)} ingredients")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    # Test with calorie target
    print("\n" + "=" * 60)
    print("2. Testing with 1800 calorie target...")
    result = estimate_nutrition(
        recipes=test_recipes,
        calorie_target=1800,
        meal_count=3
    )
    
    if result['success']:
        print(f"✓ Success! Total calories: {result['total_nutrition']['calories']}")
        print(f"\nRecommendations:")
        for rec in result.get('recommendations', []):
            print(f"  {rec}")
    
    # Test with protein target
    print("\n" + "=" * 60)
    print("3. Testing with 80g protein target...")
    result = estimate_nutrition(
        recipes=test_recipes,
        calorie_target=2000,
        protein_target=80,
        meal_count=3
    )
    
    if result['success']:
        print(f"✓ Success!")
        print(f"  Total Protein: {result['total_nutrition']['protein_g']}g")
        print(f"  Total Calories: {result['total_nutrition']['calories']} kcal")
        print(f"\nRecommendations:")
        for rec in result.get('recommendations', []):
            print(f"  {rec}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_nutrition_calculation()
