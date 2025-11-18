"""
Minimal ADK Test - Just verify imports and agent creation
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Step 1: Testing imports...")
try:
    from google.adk import Agent, Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import FunctionTool
    print("  ✓ ADK imports successful")
except ImportError as e:
    print(f"  ✗ ADK import failed: {e}")
    sys.exit(1)

print("\nStep 2: Testing gemini_setup...")
try:
    from gemini_setup import get_vision_model, get_gemini_model
    print("  ✓ gemini_setup imports successful")
except ImportError as e:
    print(f"  ✗ gemini_setup import failed: {e}")
    sys.exit(1)

print("\nStep 3: Testing vision tool...")
try:
    from adk_agent.tools import vision_tool
    print(f"  ✓ Vision tool loaded: {vision_tool.name}")
except Exception as e:
    print(f"  ✗ Vision tool failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Creating ChefByteADKAgent...")
try:
    from adk_agent import ChefByteADKAgent
    agent = ChefByteADKAgent()
    print(f"  ✓ Agent created successfully!")
    print(f"    - Name: {agent.config['agent']['name']}")
    print(f"    - Tools: {len(agent.agent.tools)}")
except Exception as e:
    print(f"  ✗ Agent creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL CHECKS PASSED!")
print("="*60)
print("\nYour ChefByte ADK agent is ready to use.")
print("\nTo test with an actual query, run:")
print("  venv/bin/python quick_test_adk.py")
print("\nOr for full tests:")
print("  venv/bin/python test_chefbyte_adk.py")
