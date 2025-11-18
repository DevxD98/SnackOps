"""
Quick test of recipe search with new database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adk_agent.tools.recipe_search_adk import search_recipes

print("🔥 Testing Recipe Search with New Database")
print("=" * 60)

# Test 1: Basic ingredient search
print("\n📋 Test 1: Search for recipes with tomato, onion, rice")
result = search_recipes(
    available_ingredients=["tomato", "onion", "rice"],
    max_missing=2
)
print(f"   Found {result['total_found']} recipes")
if result['recipes']:
    print("\n   Top 5 recipes:")
    for i, recipe in enumerate(result['recipes'][:5], 1):
        print(f"   {i}. {recipe['name']} (Match: {recipe['match_score']:.0%})")

# Test 2: Vegetarian filter
print("\n📋 Test 2: Vegetarian recipes with potato, curry")
result = search_recipes(
    available_ingredients=["potato", "curry"],
    dietary_constraints=["vegetarian"],
    max_missing=3
)
print(f"   Found {result['total_found']} vegetarian recipes")
if result['recipes']:
    print("\n   Top 5 recipes:")
    for i, recipe in enumerate(result['recipes'][:5], 1):
        print(f"   {i}. {recipe['name']} (Match: {recipe['match_score']:.0%})")

# Test 3: Vegan filter
print("\n📋 Test 3: Vegan recipes with chickpeas")
result = search_recipes(
    available_ingredients=["chickpeas", "tomato", "onion"],
    dietary_constraints=["vegan"],
    max_missing=2
)
print(f"   Found {result['total_found']} vegan recipes")
if result['recipes']:
    print("\n   Top 3 recipes:")
    for i, recipe in enumerate(result['recipes'][:3], 1):
        print(f"   {i}. {recipe['name']}")
        print(f"      Ingredients: {recipe['ingredients'][:100]}...")

# Test 4: Check database stats
print("\n📊 Database Statistics:")
import pandas as pd
recipes_df = pd.read_csv("data/recipes.csv")
print(f"   Total recipes: {len(recipes_df)}")
print(f"   Vegetarian: {recipes_df['vegetarian'].sum()}")
print(f"   Vegan: {recipes_df['vegan'].sum()}")
print(f"   Gluten-free: {recipes_df['gluten-free'].sum()}")

print("\n✅ Recipe search tests complete!")
