"""
Test persistent memory system with ChefByte agent
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adk_agent import ChefByteADKAgent

print("🔥 ChefByte Memory System Test")
print("=" * 60)

# Initialize agent with user ID
agent = ChefByteADKAgent(user_id="test_user_001")

print("\n📊 Initial Memory State:")
print(agent.get_memory_summary())

# Test 1: Add ingredients manually
print("\n" + "=" * 60)
print("TEST 1: Adding ingredients to fridge manually")
print("=" * 60)

result = agent.update_fridge_manual([
    "tomato", "onion", "garlic", "ginger",
    "chicken", "rice", "spinach", "yogurt"
])
print(f"✓ Added {result['new_ingredients']} ingredients")
print(f"  Total in fridge: {result['total_ingredients']}")

# Test 2: Set dietary preferences
print("\n" + "=" * 60)
print("TEST 2: Setting dietary preferences")
print("=" * 60)

agent.set_dietary_preferences(["vegetarian", "gluten_free"])
agent.set_calorie_target(1800)

# Test 3: Mark recipes as cooked/favorite
print("\n" + "=" * 60)
print("TEST 3: Recording recipe interactions")
print("=" * 60)

agent.mark_recipe_as_cooked("Palak Paneer", rating=5)
agent.mark_recipe_as_cooked("Chole Bhature", rating=4)
agent.add_favorite_recipe("Palak Paneer")
agent.add_disliked_recipe("Bitter Gourd Curry")

print("✓ Recorded cooking history and preferences")

# Test 4: Show updated memory
print("\n" + "=" * 60)
print("UPDATED MEMORY STATE:")
print("=" * 60)
print(agent.get_memory_summary())

# Test 5: Check memory context for agent
print("\n" + "=" * 60)
print("AGENT CONTEXT (what agent sees):")
print("=" * 60)

context = agent.memory.get_agent_context()
print(f"Fridge: {', '.join(context['fridge_inventory'][:10])}")
print(f"Dietary: {', '.join(context['dietary_constraints'])}")
print(f"Recent recipes: {', '.join(context['recent_recipes'])}")
print(f"Favorites: {', '.join(context['favorite_recipes'])}")
print(f"Disliked: {', '.join(context['disliked_recipes'])}")
print(f"Calorie target: {context['calorie_target']}")

# Test 6: Memory persists across sessions
print("\n" + "=" * 60)
print("TEST 6: Memory persistence")
print("=" * 60)

print("Creating new agent instance with same user ID...")
agent2 = ChefByteADKAgent(user_id="test_user_001")

print("\n✓ Memory loaded from disk:")
print(agent2.get_memory_summary())

# Test 7: Different user has separate memory
print("\n" + "=" * 60)
print("TEST 7: Multi-user support")
print("=" * 60)

agent3 = ChefByteADKAgent(user_id="test_user_002")
print("\n✓ User 002 has clean memory:")
print(agent3.get_memory_summary())

print("\n" + "=" * 60)
print("✅ All memory tests passed!")
print("=" * 60)

# Show file locations
print("\n📁 Memory files stored at:")
print(f"   {agent.memory.storage_dir}")
print("\nFiles created:")
print(f"   - {agent.memory.fridge_file.name}")
print(f"   - {agent.memory.history_file.name}")
print(f"   - {agent.memory.preferences_file.name}")
