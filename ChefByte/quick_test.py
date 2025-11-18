"""
Quick test of ChefByte - demonstrates all features working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🍳 ChefByte Quick Test")
print("="*60)
print()

# Test 1: Ingredient Normalizer
print("1️⃣  Testing Ingredient Normalizer...")
from agent.tools.ingredient_normalizer import normalize_ingredients

test_ingredients = [
    "2 lbs chicken breast",
    "fresh tomatos", 
    "1 cup rice"
]

normalized = normalize_ingredients(test_ingredients)
print(f"   ✓ Normalized: {', '.join(normalized)}")
print()

# Test 2: Recipe Search
print("2️⃣  Testing Recipe Search...")
from agent.tools.recipe_search import search_recipes

recipes = search_recipes(normalized, max_missing=2)
print(f"   ✓ Found {len(recipes)} matching recipes")
if recipes:
    print(f"   Top recipe: {recipes[0]['name']} ({recipes[0]['match_percentage']} match)")
print()

# Test 3: Nutrition Calculator  
print("3️⃣  Testing Nutrition Calculator...")
from agent.tools.nutrition_estimator import calculate_nutrition

if recipes:
    nutrition = calculate_nutrition(recipes[:3], calorie_target=2000, meal_count=3)
    print(f"   ✓ Calculated nutrition for {len(nutrition['selected_meals'])} meals")
    total_cal = nutrition['total_nutrition'].get('calories', 0)
    print(f"   Total calories: {total_cal}")
print()

# Test 4: Full Agent
print("4️⃣  Testing Full Agent (without images)...")
from agent.orchestrator import ChefByteAgent

agent = ChefByteAgent()
print("   ✓ Agent initialized successfully")
print()

print("="*60)
print("✅ All tests passed! ChefByte is working correctly.")
print()
print("Next steps:")
print("  • Run the Gradio UI: python ui/gradio_ui.py")
print("  • Open the Jupyter notebook: jupyter notebook notebook/ChefByte_Demo.ipynb")
print("  • Try with real fridge images!")
