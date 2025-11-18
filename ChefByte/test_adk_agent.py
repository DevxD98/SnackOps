"""
Quick Test for ChefByte ADK Agent
"""
import os
import sys

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test basic imports
print("=== Testing ADK Agent Imports ===\n")

try:
    from google.adk import Agent
    print("✓ google.adk.Agent imported")
except ImportError as e:
    print(f"✗ Failed to import google.adk.Agent: {e}")
    sys.exit(1)

try:
    from google.adk.tools import FunctionTool
    print("✓ google.adk.tools.FunctionTool imported")
except ImportError as e:
    print(f"✗ Failed to import FunctionTool: {e}")
    sys.exit(1)

try:
    from gemini_setup import get_vision_model, get_gemini_model
    print("✓ gemini_setup imported")
except ImportError as e:
    print(f"✗ Failed to import gemini_setup: {e}")
    sys.exit(1)

# Test creating a simple tool
print("\n=== Testing Simple ADK Tool ===\n")

def test_tool(message: str) -> str:
    """
    A simple test tool that echoes back a message.
    
    Args:
        message: The message to echo
    
    Returns:
        The echoed message
    """
    return f"Echo: {message}"

try:
    simple_tool = FunctionTool(test_tool)
    print(f"✓ Created FunctionTool: {simple_tool.name}")
    print(f"  Description: {simple_tool.description[:80]}...")
except Exception as e:
    print(f"✗ Failed to create FunctionTool: {e}")
    sys.exit(1)

# Test creating ADK agent with simple tool
print("\n=== Testing ADK Agent Creation ===\n")

try:
    agent = Agent(
        name="TestAgent",
        model="gemini-2.5-flash",
        description="A simple test agent",
        instruction="You are a helpful test assistant.",
        tools=[simple_tool]
    )
    print(f"✓ Created ADK Agent: {agent.name}")
    print(f"  Model: gemini-2.5-flash")
    print(f"  Tools: {len(agent.tools)}")
except Exception as e:
    print(f"✗ Failed to create ADK Agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test simple agent query
print("\n=== Testing Agent Execution ===\n")

try:
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    
    # Create runner for the agent
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="ChefByteTest",
        agent=agent,
        session_service=session_service
    )
    
    # Create a session
    session_id = "test_session_1"
    
    print(f"✓ Created Runner")
    print(f"  Session ID: {session_id}")
    print(f"  Note: ADK requires async execution or run_live() for interactive mode")
    print(f"  Skipping actual execution in this test")
    
except Exception as e:
    print(f"✗ Runner creation/execution failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
