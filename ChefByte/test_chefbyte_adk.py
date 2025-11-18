"""
Test ChefByte ADK Agent
Run this to verify the agent works correctly
"""
import os
import sys
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adk_agent import ChefByteADKAgent


async def test_basic_greeting():
    """Test 1: Basic greeting and introduction"""
    print("\n" + "="*60)
    print("TEST 1: Basic Greeting")
    print("="*60)
    
    agent = ChefByteADKAgent()
    result = await agent.run_async("Hello! Who are you and what can you help me with?")
    
    if result['success']:
        print(f"✓ Success!")
        print(f"\nResponse:\n{result['response']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result['success']


async def test_ingredient_query():
    """Test 2: Ask about ingredient extraction"""
    print("\n" + "="*60)
    print("TEST 2: Ingredient Extraction Query")
    print("="*60)
    
    agent = ChefByteADKAgent()
    result = await agent.run_async(
        "I have tomatoes, onions, rice, and chicken. "
        "What recipes can you suggest?"
    )
    
    if result['success']:
        print(f"✓ Success!")
        print(f"\nResponse:\n{result['response']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result['success']


async def test_dietary_constraints():
    """Test 3: Dietary constraints handling"""
    print("\n" + "="*60)
    print("TEST 3: Dietary Constraints")
    print("="*60)
    
    agent = ChefByteADKAgent()
    result = await agent.run_async(
        "I'm vegetarian and need high-protein meals. "
        "I have paneer, spinach, dal, and rice. What should I make?"
    )
    
    if result['success']:
        print(f"✓ Success!")
        print(f"\nResponse:\n{result['response']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result['success']


async def test_indian_cuisine_knowledge():
    """Test 4: Indian cuisine knowledge"""
    print("\n" + "="*60)
    print("TEST 4: Indian Cuisine Knowledge")
    print("="*60)
    
    agent = ChefByteADKAgent()
    result = await agent.run_async(
        "What's the difference between palak paneer and saag paneer? "
        "I have haldi, dhania, and jeera - what are these in English?"
    )
    
    if result['success']:
        print(f"✓ Success!")
        print(f"\nResponse:\n{result['response']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result['success']


async def test_meal_planning():
    """Test 5: Meal planning with calorie target"""
    print("\n" + "="*60)
    print("TEST 5: Meal Planning")
    print("="*60)
    
    agent = ChefByteADKAgent()
    result = await agent.run_async(
        "I want to plan 3 meals for today with a total of 1800 calories. "
        "I prefer North Indian food and I'm vegetarian. "
        "Available ingredients: rice, dal, paneer, tomatoes, onions, spinach, "
        "potatoes, yogurt, and common spices."
    )
    
    if result['success']:
        print(f"✓ Success!")
        print(f"\nResponse:\n{result['response']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result['success']


async def test_conversation_continuity():
    """Test 6: Multi-turn conversation"""
    print("\n" + "="*60)
    print("TEST 6: Conversation Continuity")
    print("="*60)
    
    agent = ChefByteADKAgent()
    session_id = "test_session_123"
    
    # Turn 1
    print("\n[Turn 1] User: What can I make with chicken and rice?")
    result1 = await agent.run_async(
        "What can I make with chicken and rice?",
        session_id=session_id
    )
    if result1['success']:
        print(f"Agent: {result1['response'][:200]}...")
    
    # Turn 2
    print("\n[Turn 2] User: Make it vegetarian instead")
    result2 = await agent.run_async(
        "Make it vegetarian instead",
        session_id=session_id
    )
    if result2['success']:
        print(f"Agent: {result2['response'][:200]}...")
        print(f"✓ Conversation continuity working!")
    else:
        print(f"✗ Failed: {result2.get('error')}")
    
    return result2['success']


def test_sync_wrapper():
    """Test 7: Synchronous wrapper"""
    print("\n" + "="*60)
    print("TEST 7: Synchronous Wrapper")
    print("="*60)
    
    agent = ChefByteADKAgent()
    result = agent.run("Quick test: Can you help me with meal planning?")
    
    if result['success']:
        print(f"✓ Sync wrapper works!")
        print(f"Response: {result['response'][:150]}...")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result['success']


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("ChefByte ADK Agent Test Suite")
    print("="*60)
    
    results = []
    
    # Run async tests
    results.append(await test_basic_greeting())
    results.append(await test_ingredient_query())
    results.append(await test_dietary_constraints())
    results.append(await test_indian_cuisine_knowledge())
    results.append(await test_meal_planning())
    results.append(await test_conversation_continuity())
    
    # Run sync test
    results.append(test_sync_wrapper())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    print("Starting ChefByte ADK Agent tests...")
    print("Note: This requires a valid GOOGLE_API_KEY in your .env file")
    print()
    
    # Run tests
    asyncio.run(run_all_tests())
